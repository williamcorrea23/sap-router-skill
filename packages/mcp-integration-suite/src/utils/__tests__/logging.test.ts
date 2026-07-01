import fs from 'fs/promises';
import path from 'path';
import { writeToLog, writeToErrLog } from '../logging';
import { projPath } from '../..'; // Assuming projPath is exported from src/index.ts

describe('Logging Utility Functions', () => {
    const logFilePath = path.resolve(projPath, 'serverlog.txt');
    const errLogFilePath = path.resolve(projPath, 'errorlog.txt');

    // Helper to read last line of a file
    const readLastLine = async (filePath: string): Promise<string | null> => {
        try {
            const content = await fs.readFile(filePath, 'utf-8');
            const lines = content.trim().split('\n');
            return lines.length > 0 ? lines[lines.length - 1] : null;
        } catch (error: any) {
            if (error.code === 'ENOENT') {
                return null; // File doesn't exist
            }
            throw error;
        }
    };

    // Clear log files before each test to prevent interference
    beforeEach(async () => {
        try { await fs.writeFile(logFilePath, ''); } catch (e) {}
        try { await fs.writeFile(errLogFilePath, ''); } catch (e) {}
    });

    it('writeToLog should write a formatted message to serverlog.txt', async () => {
        const uniqueMessage1 = `Unique log message 1 ${Date.now()}`;
        const uniqueMessage2 = `Unique log message 2 ${Date.now()}`;
        const testObject = { logId: 123, payload: 'log payload' };
        const expectedObjectString = "{ logId: 123, payload: 'log payload' }"; // How util.format likely outputs

        writeToLog(uniqueMessage1);
        writeToLog(testObject);
        writeToLog(uniqueMessage2);

        // Wait a bit longer for potentially multiple writes
        await new Promise(resolve => setTimeout(resolve, 100));

        const logContent = await fs.readFile(logFilePath, 'utf-8');
        expect(logContent).toContain(uniqueMessage1);
        expect(logContent).toContain(expectedObjectString);
        expect(logContent).toContain(uniqueMessage2);
    });

    it('writeToErrLog should write a formatted message to errorlog.txt', async () => {
        const uniqueErrorMessage1 = `Unique error message 1 ${Date.now()}`;
        const uniqueErrorMessage2 = `Unique error message 2 ${Date.now()}`;
        const testErrorObject = new Error('Specific error occurred');
        const expectedErrorString = 'Error: Specific error occurred';

        writeToErrLog(uniqueErrorMessage1);
        writeToErrLog(testErrorObject);
        writeToErrLog(uniqueErrorMessage2);

        // Wait a bit longer
        await new Promise(resolve => setTimeout(resolve, 100));

        const errLogContent = await fs.readFile(errLogFilePath, 'utf-8');
        expect(errLogContent).toContain(uniqueErrorMessage1);
        expect(errLogContent).toContain(expectedErrorString);
        // Check for stack trace part as well
        expect(errLogContent).toContain('at Object.<anonymous>');
        expect(errLogContent).toContain(uniqueErrorMessage2);
    });
});
