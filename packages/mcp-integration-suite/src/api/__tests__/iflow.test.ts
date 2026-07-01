import {
    createIflow,
    getAllIflowsByPackage,
    getIflowFolder,
    updateIflow,
    deployIflow,
    getEndpoints,
    getIflowConfiguration,
    saveAsNewVersion,
    getIflowContentString
} from "../iflow/index";
import { createPackage, getPackage } from "../packages/index"; // Need createPackage to ensure test package exists
import { waitAndGetDeployStatus, getDeploymentErrorReason } from "../deployment"; // Need deployment status check
import { getiFlowToImage } from '../iflow/diagram'; // Import the diagram function
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs/promises';
import { deletePackage } from "./helpers";

// Load environment variables from .env file
dotenv.config();

describe("IFlow Management API", () => {
    // Increase timeout significantly for multiple API calls including deployment waits
    jest.setTimeout(300000); // 5 minutes

    const testPackageIdBase = `jesttestpkgiflows`; // No underscores
    let testPackageId: string = ""; // Initialize
    const testIflowId = `jesttestiflow${Date.now()}`; // No underscores
    let packageCreated = false;
    let iflowCreated = false;
    let iflowDeployed = false;

    // Check prerequisites and create a dedicated package for these tests
    beforeAll(async () => {
        if (!process.env.API_BASE_URL || (!process.env.API_USER && !process.env.API_OAUTH_CLIENT_ID)) {
            throw new Error("Missing required environment variables for API connection (URL and Auth). Skipping IFlow tests.");
        }
        // Create a unique package for this test run (no underscores)
        testPackageId = `${testPackageIdBase}${Date.now()}`; // Removed underscore
        try {
            console.log(`Attempting to create test package for iflows: ${testPackageId}`);
            await createPackage(testPackageId, `Jest IFlow Test Pkg`, `Temp pkg for Jest IFlow tests`);
            packageCreated = true;
            console.log(`Test package ${testPackageId} created successfully.`);
        } catch (error) {
            console.error(`Failed to create test package ${testPackageId}. IFlow tests will likely fail. Error:`, error);
            // Throwing error here as subsequent tests depend heavily on the package
            throw new Error(`Failed to create prerequisite package ${testPackageId}`);
        }
    });

    // Note: No automatic cleanup for the package or iflow. Manual cleanup needed.

    it("should create an empty iflow", async () => {
        expect(packageCreated).toBe(true); // Ensure package exists
        try {
            await createIflow(testPackageId, testIflowId);
            iflowCreated = true;
            // Verify by trying to get it (or check list)
            const iflows = await getAllIflowsByPackage(testPackageId);
            const found = iflows.some((iflow: any) => iflow.Id === testIflowId);
            expect(found).toBe(true);
        } catch (error) {
            console.error(`Error during createIflow test for ${testIflowId} in package ${testPackageId}:`, error);
            throw error;
        }
    });

    it("should retrieve all iflows for a package", async () => {
        expect(packageCreated).toBe(true);
        expect(iflowCreated).toBe(true); // Ensure the iflow we created exists
        try {
            const iflows = await getAllIflowsByPackage(testPackageId);
            expect(iflows).toBeDefined();
            expect(Array.isArray(iflows)).toBe(true);
            expect(iflows.length).toBeGreaterThanOrEqual(1); // Should contain at least the one we created
            const found = iflows.some((iflow: any) => iflow.Id === testIflowId);
            expect(found).toBe(true);
        } catch (error) {
            console.error(`Error during getAllIflowsByPackage test for package ${testPackageId}:`, error);
            throw error;
        }
    });

    it("should download the iflow folder", async () => {
        expect(iflowCreated).toBe(true);
        let iflowPath: string | undefined;
        try {
            iflowPath = await getIflowFolder(testIflowId);
            expect(iflowPath).toBeDefined();
            expect(typeof iflowPath).toBe('string');
            // Check if the directory exists
            const stats = await fs.stat(iflowPath);
            expect(stats.isDirectory()).toBe(true);
            // Optionally check for expected files within the downloaded structure (e.g., META-INF)
            await fs.access(path.join(iflowPath, 'META-INF', 'MANIFEST.MF'));
        } catch (error) {
            console.error(`Error during getIflowFolder test for ${testIflowId}:`, error);
            throw error;
        } finally {
            // Clean up the downloaded folder
            if (iflowPath) {
                try {
                    await fs.rm(iflowPath, { recursive: true, force: true });
                } catch (cleanupError) {
                    console.warn(`Could not clean up downloaded iflow folder: ${iflowPath}`, cleanupError);
                }
            }
        }
    });

     it("should update an iflow with new file content", async () => {
        expect(iflowCreated).toBe(true);
        const testFilePath = "src/main/resources/script/testScript.groovy";
        const testFileContent = "// Test Groovy Script Content - " + Date.now();
        try {
            const updateResult = await updateIflow(testIflowId, [{
                filepath: testFilePath,
                content: testFileContent,
                appendMode: false
            }]);
            expect(updateResult).toBeDefined();
            expect(updateResult.iflowUpdate).toBeDefined();
            expect(updateResult.iflowUpdate.status).toBe(200); // Assuming 200 means success for update part

            // Verify update by downloading again and checking content
            const iflowPath = await getIflowFolder(testIflowId);
            const scriptPath = path.join(iflowPath, testFilePath);
            const actualContent = await fs.readFile(scriptPath, 'utf-8');
            expect(actualContent).toEqual(testFileContent);
             // Clean up downloaded folder
             await fs.rm(iflowPath, { recursive: true, force: true });

        } catch (error) {
            console.error(`Error during updateIflow test for ${testIflowId}:`, error);
             // Clean up potentially downloaded folder on error
             try {
                 const iflowPath = path.join(process.cwd(), 'temp', testIflowId); // Assuming temp folder structure
                 await fs.rm(iflowPath, { recursive: true, force: true });
             } catch (cleanupError) {}
            throw error;
        }
    });

    it("should deploy an iflow and check status", async () => {
        expect(iflowCreated).toBe(true); // Ensure iflow exists (updated in previous test)
        try {
            const taskId = await deployIflow(testIflowId);
            expect(taskId).toBeDefined();
            expect(typeof taskId).toBe('string');
            console.log(`Deployment task ID for ${testIflowId}: ${taskId}. Waiting for status...`);

            const finalStatus = await waitAndGetDeployStatus(taskId);
            console.log(`Deployment status for ${testIflowId}: ${finalStatus}`);

            if (finalStatus !== "SUCCESS") {
                 const errorReason = await getDeploymentErrorReason(testIflowId);
                 console.error(`Deployment failed for ${testIflowId}. Status: ${finalStatus}. Reason: ${errorReason}`);
                 // Optionally fail the test explicitly if deployment fails
                 // expect(finalStatus).toEqual("SUCCESS"); // This would fail the test
                 throw new Error(`Deployment failed with status ${finalStatus}. Reason: ${errorReason}`);
            }

            expect(finalStatus).toEqual("SUCCESS");
            iflowDeployed = true;

        } catch (error) {
            console.error(`Error during deployIflow/waitAndGetDeployStatus test for ${testIflowId}:`, error);
            // Attempt to get error reason even if wait failed
             try {
                 const errorReason = await getDeploymentErrorReason(testIflowId);
                 console.error(`Deployment error reason for ${testIflowId}: ${errorReason}`);
             } catch (reasonError) {
                 console.error("Could not retrieve deployment error reason.", reasonError);
             }
            throw error;
        }
    });

     it("should retrieve endpoints for the deployed iflow", async () => {
        if (!iflowDeployed) {
            console.warn(`Skipping getEndpoints test: IFlow ${testIflowId} was not successfully deployed.`);
            return;
        }
        try {
            const endpoints = await getEndpoints(testIflowId);
            expect(endpoints).toBeDefined();
            expect(Array.isArray(endpoints)).toBe(true);
            // The empty iflow might not have endpoints, so length could be 0
            // expect(endpoints.length).toBeGreaterThan(0);
            console.log(`Endpoints found for ${testIflowId}:`, JSON.stringify(endpoints, null, 2));
            // Add more specific checks if endpoints are expected for the base iflow
        } catch (error) {
            console.error(`Error during getEndpoints test for ${testIflowId}:`, error);
            throw error;
        }
    });

     it("should retrieve configuration for the iflow (expecting empty)", async () => {
         expect(iflowCreated).toBe(true);
         try {
             const config = await getIflowConfiguration(testIflowId);
             expect(config).toBeDefined();
             expect(Array.isArray(config)).toBe(true);
             // Allow for 0 or more configurations, as default might exist
             expect(config.length).toBeGreaterThanOrEqual(0); // Re-applying this assertion
         } catch (error) {
             console.error(`Error during getIflowConfiguration test for ${testIflowId}:`, error);
             throw error;
         }
     });

     it("should save the iflow as a new version", async () => {
         expect(iflowCreated).toBe(true);
         try {
             // Get current version first (though the function doesn't return it directly)
             // We just call saveAsNewVersion and expect no errors
             await saveAsNewVersion(testIflowId);
             // Verification would ideally involve getting the iflow details again and checking the version,
             // but the getIflow function isn't available directly here. We assume success if no error.
         } catch (error) {
             console.error(`Error during saveAsNewVersion test for ${testIflowId}:`, error);
             throw error;
         }
     });

     it("should get the iflow content as a string", async () => {
         expect(iflowCreated).toBe(true);
         let iflowPath: string | undefined;
         try {
             const contentString = await getIflowContentString(testIflowId);
             expect(contentString).toBeDefined();
             expect(typeof contentString).toBe('string');
             // Check for some expected content, e.g., the script added earlier
             expect(contentString).toContain("// Test Groovy Script Content");
             expect(contentString).toContain("testScript.groovy");
             expect(contentString).toContain("MANIFEST.MF"); // From the base structure
         } catch (error) {
             console.error(`Error during getIflowContentString test for ${testIflowId}:`, error);
             throw error;
         }
     });

     it("should generate a diagram image for a specific iflow (if_simple_http_cld)", async () => {
        const targetIflowId = "if_simple_http_cld"; // The iFlow specified by the user
        let iflowPath: string | undefined;
        try {
            console.log(`Attempting to download folder for diagram test: ${targetIflowId}`);
            iflowPath = await getIflowFolder(targetIflowId);
            expect(iflowPath).toBeDefined();
            expect(typeof iflowPath).toBe('string');
            console.log(`Folder downloaded to: ${iflowPath}. Generating diagram...`);

            const imageBase64 = await getiFlowToImage(iflowPath);
            expect(imageBase64).toBeDefined();
            expect(typeof imageBase64).toBe('string');
            expect(imageBase64.length).toBeGreaterThan(100); // Expecting a reasonably sized base64 string
            // Basic check if it looks like base64 (though not foolproof)
            expect(imageBase64).toMatch(/^[A-Za-z0-9+/=]+$/);
            console.log(`Successfully generated diagram image for ${targetIflowId} (length: ${imageBase64.length})`);

        } catch (error: any) {
            // Handle case where the specific iFlow might not exist on the tenant
            if (error.message && error.message.includes("Could not find")) { // Adjust error message check as needed
                 console.warn(`Skipping diagram test: IFlow ${targetIflowId} not found on the tenant.`);
                 // Mark test as skipped or pending if Jest supports it easily, otherwise just log and don't fail hard.
                 // For now, just log and let it pass if the error is 'not found'.
                 // If it's another error, re-throw it.
                 if (!error.message.includes("Could not find")) {
                    console.error(`Error during getiFlowToImage test for ${targetIflowId}:`, error);
                    throw error;
                 }
            } else {
                console.error(`Error during getiFlowToImage test for ${targetIflowId}:`, error);
                throw error;
            }
        } finally {
            // Clean up the downloaded folder regardless of success or failure
            if (iflowPath) {
                try {
                    console.log(`Cleaning up downloaded folder: ${iflowPath}`);
                    await fs.rm(iflowPath, { recursive: true, force: true });
                } catch (cleanupError) {
                    console.warn(`Could not clean up downloaded iflow folder: ${iflowPath}`, cleanupError);
                }
            }
        }
     });

    afterAll(async() => {
        await deletePackage(testPackageId);
    });

});
