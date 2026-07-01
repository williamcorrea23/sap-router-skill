import { MiddlewareManager } from '../middleware';
import { z } from 'zod';

describe('MiddlewareManager', () => {
    let manager: MiddlewareManager;
    let executionOrder: number[];
    let callParams: { name: string, params: z.ZodRawShape } | null;

    // Middleware function factory for testing order
    const createTestMiddleware = (id: number): ((next: () => Promise<void>, name: string, params: z.ZodRawShape) => Promise<void>) => {
        return async (next, name, params) => {
            executionOrder.push(id); // Record execution order
            callParams = { name, params }; // Record params passed to middleware
            await next(); // Call the next middleware
            executionOrder.push(-id); // Record when middleware finishes
        };
    };

    beforeEach(() => {
        manager = new MiddlewareManager();
        executionOrder = [];
        callParams = null;
    });

    it('should execute middlewares in the order they were added', async () => {
        const middleware1 = createTestMiddleware(1);
        const middleware2 = createTestMiddleware(2);
        const middleware3 = createTestMiddleware(3);

        manager.use(middleware1);
        manager.use(middleware2);
        manager.use(middleware3);

        const testName = 'testTool';
        const testParams = { param1: z.string() };

        await manager.execute(testName, testParams);

        // Check execution order (1 starts, 2 starts, 3 starts, 3 ends, 2 ends, 1 ends)
        expect(executionOrder).toEqual([1, 2, 3, -3, -2, -1]);
    });

    it('should pass name and params to each middleware', async () => {
        const middleware1 = createTestMiddleware(1);
        manager.use(middleware1);

        const testName = 'anotherTool';
        const testParams = { argA: z.number(), argB: z.boolean() };

        await manager.execute(testName, testParams);

        // Check if the last middleware called received the correct parameters
        expect(callParams).not.toBeNull();
        expect(callParams?.name).toEqual(testName);
        expect(callParams?.params).toEqual(testParams);
    });

    it('should handle execution with no middlewares added', async () => {
        const testName = 'noMiddlewareTool';
        const testParams = {};

        // Expect execute to complete without errors and without changing executionOrder
        await expect(manager.execute(testName, testParams)).resolves.not.toThrow();
        expect(executionOrder).toEqual([]);
    });

    it('should allow middleware to modify context or perform actions before calling next', async () => {
        let preNextFlag = false;
        let postNextFlag = false;

        const modifyingMiddleware = async (next: () => Promise<void>) => {
            // Action before next()
            preNextFlag = true;
            expect(postNextFlag).toBe(false); // Ensure post-action hasn't happened yet
            await next();
            // Action after next()
            postNextFlag = true;
            expect(preNextFlag).toBe(true); // Ensure pre-action happened
        };

        manager.use(modifyingMiddleware);
        await manager.execute('modifyTest', {});

        expect(preNextFlag).toBe(true);
        expect(postNextFlag).toBe(true);
    });
});

// Basic tests for McpServerWithMiddleware (integration might require more complex mocking)
// describe('McpServerWithMiddleware', () => {
//     // TODO: Add tests if possible without extensive mocking of McpServer internals
//     // Example: Verify 'use' adds middleware, verify 'registerTool' wraps handler
//     it.todo('should register middleware using use()');
//     it.todo('registerTool should wrap the original handler');
// });
