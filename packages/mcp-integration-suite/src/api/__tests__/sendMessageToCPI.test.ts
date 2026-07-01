import { sendRequestToCPI } from "../messages/sendMessageToCPI";
import { getEndpoints } from "../iflow/index"; // To potentially find a real endpoint
import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

describe("Send Message to CPI API", () => {
    // Increase timeout for network requests
    jest.setTimeout(30000); // 30 seconds

    // Check prerequisites before running tests
    beforeAll(() => {
        if (!process.env.CPI_BASE_URL || !process.env.CPI_OAUTH_CLIENT_ID || !process.env.CPI_OAUTH_CLIENT_SECRET || !process.env.CPI_OAUTH_TOKEN_URL) {
            // Skip all tests in this suite if CPI runtime env vars are missing
            throw new Error("Missing required environment variables for CPI connection (CPI_BASE_URL, CPI_OAUTH...). Skipping Send Message tests.");
        }
    });

    it("should attempt to send a GET request and handle the response status", async () => {
        const testPath = `/http/jest_test_nonexistent_endpoint_${Date.now()}`; // Use a likely non-existent path
        const method = "GET";
        const contentType = "application/json"; // Not relevant for GET body, but required by function

        try {
            const result = await sendRequestToCPI(testPath, method, contentType);

            expect(result).toBeDefined();
            expect(result.status).toBeDefined();
            expect(typeof result.status).toBe('number');
            expect(result.response).toBeDefined(); // Response body might be HTML error page, etc.

            // We expect a 404 Not Found for a non-existent endpoint
            // Note: Depending on CPI configuration, other errors like 401/403 might occur if auth fails,
            // or even 200 if there's a catch-all endpoint. 404 is the most likely expectation.
            expect(result.status).toEqual(404);

            console.log(`sendRequestToCPI to ${testPath} completed with status: ${result.status}`);

        } catch (error) {
            console.error(`Error during sendRequestToCPI test to ${testPath}:`, error);
            throw error;
        }
    });

    it("should attempt to send a POST request and handle the response status", async () => {
        // Sending to the same non-existent path, expecting 404
        const testPath = `/http/jest_test_nonexistent_endpoint_post_${Date.now()}`;
        const method = "POST";
        const contentType = "application/json";
        const body = JSON.stringify({ test: "data", timestamp: Date.now() });

         try {
            const result = await sendRequestToCPI(testPath, method, contentType, body);

            expect(result).toBeDefined();
            expect(result.status).toBeDefined();
            expect(typeof result.status).toBe('number');
            expect(result.response).toBeDefined();

            // Expect 404 Not Found
            expect(result.status).toEqual(404);

            console.log(`sendRequestToCPI (POST) to ${testPath} completed with status: ${result.status}`);

        } catch (error) {
            console.error(`Error during sendRequestToCPI (POST) test to ${testPath}:`, error);
            throw error;
        }
    });

    // Add a test that tries to hit a potentially real endpoint (if if_echo_mapping was deployed)
    // This is less reliable as it depends on previous test suites' success
    // Skipping due to flakiness
    it.skip("should attempt to send a POST request to the echo mapping iflow (if available)", async () => {
        const echoIflowId = "if_simple_http_cld";
        let echoEndpointPath: string | undefined = undefined;

        // Try to find the endpoint dynamically - might fail if not deployed or endpoint format changes
        try {
            const endpoints = await getEndpoints(echoIflowId);
            // Cast to any to access the dynamically added URL property
            const firstEndpoint = endpoints?.[0] as any;
            if (firstEndpoint && firstEndpoint.URL) {
                 // Extract path from URL - assumes format like https://host/http/path
                 const urlParts = new URL(firstEndpoint.URL);
                 if (urlParts.pathname.startsWith('/http/')) {
                    echoEndpointPath = urlParts.pathname;
                    console.log(`Found potential echo endpoint: ${echoEndpointPath}`);
                 }
            }
        } catch (e) {
            console.warn(`Could not retrieve endpoint for ${echoIflowId}. Skipping echo test. Error: ${e}`);
        }

        if (!echoEndpointPath) {
            console.warn(`Skipping echo test as endpoint for ${echoIflowId} could not be determined.`);
            return; // Skip test if endpoint not found
        }

        const method = "POST";
        const contentType = "application/xml"; // Echo iflow likely expects XML for mapping
        const body = `<TestRequest><Data>Hello Echo ${Date.now()}</Data></TestRequest>`;

         try {
            const result = await sendRequestToCPI(echoEndpointPath, method, contentType, body);

            expect(result).toBeDefined();
            expect(result.status).toBeDefined();
            // Expect success (e.g., 200) if the iflow exists and processes the request
            // It might return other codes (e.g., 500 if mapping fails)
            expect(result.status).toBeGreaterThanOrEqual(200);
            expect(result.status).toBeLessThan(300); // General success range
            expect(result.response).toBeDefined();
            // Check if response contains some part of the input (echo behavior)
            expect(result.response).toContain("Hello Echo");


            console.log(`sendRequestToCPI (POST) to ${echoEndpointPath} completed with status: ${result.status}`);

        } catch (error) {
            console.error(`Error during sendRequestToCPI (POST) test to ${echoEndpointPath}:`, error);
            throw error;
        }
    });

});
