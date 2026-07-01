import {
    getMessages,
    getMessagesCount,
    getMessageMedia, // Note: Testing this requires a known message with a known attachment ID
    createMappingTestIflow
} from "../messages/messageLogs";
import { createPackage } from "../packages/index"; // Need createPackage
import { getAllIflowsByPackage, deployIflow } from "../iflow/index"; // Need to check iflow creation/deployment
import { waitAndGetDeployStatus, getDeploymentErrorReason } from "../deployment"; // Need deployment status check
import dotenv from 'dotenv';
import moment from 'moment';
import { deletePackage } from "./helpers";

// Load environment variables from .env file
dotenv.config();

describe("Message Log API", () => {
    // Increase timeout significantly
    jest.setTimeout(300000); // 5 minutes

    const testPackageIdBase = `jesttestpkgmsglogs`; // No underscores
    let testPackageId: string = ""; // Initialize
    const testIflowId = "if_echo_mapping"; // Specific ID used by createMappingTestIflow
    let packageCreated = false;
    let testIflowCreated = false;
    let testIflowDeployed = false;

    // Check prerequisites and create a dedicated package for these tests
    beforeAll(async () => {
        if (!process.env.API_BASE_URL || (!process.env.API_USER && !process.env.API_OAUTH_CLIENT_ID)) {
            throw new Error("Missing required environment variables for API connection (URL and Auth). Skipping Message Log tests.");
        }
        // Create a unique package for this test run (no underscores)
        testPackageId = testPackageIdBase; // Removed underscore
        try {
            console.log(`Attempting to create test package for message logs: ${testPackageId}`);
            await createPackage(testPackageId, `Jest MsgLog Test Pkg`, `Temp pkg for Jest MsgLog tests`);
            packageCreated = true;
            console.log(`Test package ${testPackageId} created successfully.`);
        } catch (error) {
            console.error(`Failed to create test package ${testPackageId}. Message Log tests will likely fail. Error:`, error);
            throw new Error(`Failed to create prerequisite package ${testPackageId}`);
        }
    });

    // Note: No automatic cleanup for the package or iflow. Manual cleanup needed.

    it("should create the mapping test iflow 'if_echo_mapping'", async () => {
        expect(packageCreated).toBe(true); // Ensure package exists
        try {
            await createMappingTestIflow(testPackageId);
            testIflowCreated = true;
            // Verify by checking the list of iflows in the package
            const iflows = await getAllIflowsByPackage(testPackageId);
            const found = iflows.some((iflow: any) => iflow.Id === testIflowId);
            expect(found).toBe(true);
            console.log(`IFlow ${testIflowId} created in package ${testPackageId}.`);

            // Also deploy it for subsequent tests if needed (e.g., for getMessages)
            console.log(`Attempting to deploy ${testIflowId}...`);
            const taskId = await deployIflow(testIflowId);
            const status = await waitAndGetDeployStatus(taskId);
             if (status !== "SUCCESS") {
                 const reason = await getDeploymentErrorReason(testIflowId);
                 throw new Error(`Deployment of ${testIflowId} failed. Status: ${status}. Reason: ${reason}`);
             }
             testIflowDeployed = true;
             console.log(`IFlow ${testIflowId} deployed successfully.`);

        } catch (error) {
            console.error(`Error during createMappingTestIflow test for package ${testPackageId}:`, error);
            // Attempt to get error reason if deployment might have failed
            try {
                 const errorReason = await getDeploymentErrorReason(testIflowId);
                 console.error(`Deployment error reason for ${testIflowId}: ${errorReason}`);
             } catch (reasonError) {}
            throw error;
        }
    });

    it("should count messages within a time range", async () => {
        // This test assumes there might be *some* messages in the system.
        // It's hard to guarantee messages exist without sending one first.
        try {
            const now = moment();
            const fiveMinutesAgo = moment().subtract(5, 'minutes');
            const count = await getMessagesCount({
                LogStart: fiveMinutesAgo.toISOString(),
                LogEnd: now.toISOString()
            });
            expect(count).toBeDefined();
            expect(typeof count).toBe('number');
            expect(count).toBeGreaterThanOrEqual(0); // Count can be 0
            console.log(`Found ${count} messages in the last 5 minutes.`);
        } catch (error) {
            console.error(`Error during getMessagesCount test:`, error);
            throw error;
        }
    });

    it("should retrieve messages with filters (last 5 mins, limit 50)", async () => {
        // Similar to count, assumes some messages might exist.
        try {
            const now = moment();
            const fiveMinutesAgo = moment().subtract(5, 'minutes');
            const messages = await getMessages({
                LogStart: fiveMinutesAgo.toISOString(),
                LogEnd: now.toISOString()
                // Optionally add status or iflow filter if needed for more specific tests
                // status: ["COMPLETED", "FAILED"],
                // integrationFlowId: testIflowId // Only if we sent a message to it
            });
            expect(messages).toBeDefined();
            expect(Array.isArray(messages)).toBe(true);
            expect(messages.length).toBeLessThanOrEqual(50); // Due to internal limit in getMessages
            console.log(`Retrieved ${messages.length} messages from the last 5 minutes.`);
            // Can add more checks here if specific messages are expected
            if (messages.length > 0) {
                expect(messages[0].messageGuid).toBeDefined();
                // Check structure of retrieved messages if needed
            }
        } catch (error) {
            console.error(`Error during getMessages test:`, error);
            throw error;
        }
    });

    it("should retrieve a specific error message log by GUID", async () => {
        const messageGuid = 'AGfvA8x0AEIbl1ys-9uF2KYDy_QR';
        const errorStatuses = ["RETRY", "FAILED", "ABANDONED", "ESCALATED", "DISCARDED"]; // From messageLogs.ts

        try {
            const messages = await getMessages({ msgGUID: messageGuid });

            expect(messages).toBeDefined();
            expect(Array.isArray(messages)).toBe(true);
            expect(messages).toHaveLength(1); // Should find exactly one message

            const message = messages[0];
            expect(message.messageGuid).toEqual(messageGuid);
            expect(message.status).toBeDefined();
            
            expect(errorStatuses).toContain(message.status); // Check if it's an error status
            expect(message.ErrorInformationValue).toBeDefined(); // Error details should be fetched
            expect(typeof message.ErrorInformationValue).toBe('string');
            expect(message.ErrorInformationValue).not.toBe(''); // Error details should not be empty
            console.log(`Successfully retrieved error message log ${messageGuid}. Status: ${message.status}`);

        } catch (error) {
            console.error(`Error during getMessages test for specific GUID ${messageGuid}:`, error);
            throw error;
        }
    });

    it("should retrieve a specific error message log with attachments by GUID", async () => {
        const messageGuid = 'AGfpKafrrEtNpKvhiZL6yO2oHucr';
        const errorStatuses = ["RETRY", "FAILED", "ABANDONED", "ESCALATED", "DISCARDED"]; // From messageLogs.ts

        try {
            const messages = await getMessages({ msgGUID: messageGuid });

            expect(messages).toBeDefined();
            expect(Array.isArray(messages)).toBe(true);
            expect(messages).toHaveLength(1); // Should find exactly one message

            const message = messages[0];
            expect(message.messageGuid).toEqual(messageGuid);
            expect(message.status).toBeDefined();
            // @ts-ignore - status could be null theoretically but should exist for a real message
            expect(errorStatuses).toContain(message.status); // Check if it's an error status
            expect(message.ErrorInformationValue).toBeDefined(); // Error details should be fetched
            expect(typeof message.ErrorInformationValue).toBe('string');
            expect(message.ErrorInformationValue).not.toBe(''); // Error details should not be empty

            // Check for attachments
            expect(message.attachments).toBeDefined();
            expect(Array.isArray(message.attachments)).toBe(true);
            expect(message.attachments.length).toBeGreaterThan(0); // Should have at least one attachment entry

            // Check for fetched attachment files (content) - ensure the array exists and has items first
            expect(message.messageAttachementFiles).toBeDefined(); // Check if the array itself exists
            // Use type assertion or check to satisfy TypeScript
            if (message.messageAttachementFiles) {
                expect(Array.isArray(message.messageAttachementFiles)).toBe(true);
                expect(message.messageAttachementFiles.length).toBeGreaterThan(0); // Should have fetched content
                expect(message.messageAttachementFiles[0]).toBeDefined(); // Check if the first element exists
                expect(message.messageAttachementFiles[0].data).toBeDefined(); // Check if data exists for the first attachment
                expect(typeof message.messageAttachementFiles[0].data).toBe('string');
                expect(message.messageAttachementFiles[0].data).not.toBe(''); // Attachment content should not be empty
            } else {
                // Fail the test if messageAttachementFiles is unexpectedly undefined
                throw new Error("Expected messageAttachementFiles to be defined for this message GUID.");
            }


            console.log(`Successfully retrieved error message log ${messageGuid} with attachments. Status: ${message.status}`);

        } catch (error) {
            console.error(`Error during getMessages test for specific GUID ${messageGuid} with attachments:`, error);
            throw error;
        }
    });


    afterAll(async() => {
        await deletePackage(testPackageId);
    });

});
