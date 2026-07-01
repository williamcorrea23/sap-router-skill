import fs from 'fs/promises';
import path from 'path';
import AdmZip from 'adm-zip';
import { extractToFolder, folderToZipBuffer } from '../zip';
import { rimraf } from 'rimraf'; // Used for cleanup

// Helper function to create a temporary directory structure for testing
const createTestDir = async (basePath: string, structure: { [key: string]: string | object }): Promise<void> => {
    for (const name in structure) {
        const currentPath = path.join(basePath, name);
        const content = structure[name];
        if (typeof content === 'string') {
            await fs.writeFile(currentPath, content, 'utf-8');
        } else if (typeof content === 'object') {
            await fs.mkdir(currentPath, { recursive: true });
            await createTestDir(currentPath, content as { [key: string]: string | object });
        }
    }
};

// Helper function to verify directory structure and content
const verifyTestDir = async (basePath: string, expectedStructure: { [key: string]: string | object }): Promise<void> => {
    for (const name in expectedStructure) {
        const currentPath = path.join(basePath, name);
        const expectedContent = expectedStructure[name];
        const stats = await fs.stat(currentPath); // Throws if path doesn't exist

        if (typeof expectedContent === 'string') {
            expect(stats.isFile()).toBe(true);
            const actualContent = await fs.readFile(currentPath, 'utf-8');
            expect(actualContent).toEqual(expectedContent);
        } else if (typeof expectedContent === 'object') {
            expect(stats.isDirectory()).toBe(true);
            await verifyTestDir(currentPath, expectedContent as { [key: string]: string | object });
        }
    }
    // Optional: Check if there are extra files/dirs not in expectedStructure
    const actualEntries = await fs.readdir(basePath);
    expect(actualEntries.length).toEqual(Object.keys(expectedStructure).length);
};


describe('ZIP Utility Functions', () => {
    const tempBaseDir = path.join(__dirname, 'temp_zip_test'); // Base for test dirs
    const sourceDir = path.join(tempBaseDir, 'source');
    const extractDirBase = path.join(tempBaseDir, 'extracted');
    const testStructure = {
        'file1.txt': 'Hello World!',
        'subdir': {
            'file2.txt': 'Another file.',
            'nested': {
                'file3.json': '{ "data": 123 }'
            }
        },
        'empty_dir': {}
    };

    // Create base temp directory before all tests
    beforeAll(async () => {
        await rimraf(tempBaseDir); // Clean up any previous runs
        await fs.mkdir(tempBaseDir, { recursive: true });
    });

    // Clean up the base temp directory after all tests
    afterAll(async () => {
        await rimraf(tempBaseDir);
    });

    // Clean up source and extracted dirs before each test (relevant for extractToFolder)
    beforeEach(async () => {
        await rimraf(sourceDir);
        await rimraf(extractDirBase); // Clean potential extraction targets
        await fs.mkdir(sourceDir, { recursive: true });
        await fs.mkdir(extractDirBase, { recursive: true });
        // Recreate source structure before each test
        await createTestDir(sourceDir, testStructure);
    });

    it('should zip a folder structure into a buffer', async () => {
        const zipBuffer = await folderToZipBuffer(sourceDir);
        expect(zipBuffer).toBeInstanceOf(Buffer);
        expect(zipBuffer.length).toBeGreaterThan(0);

        // Optional: Verify buffer content using AdmZip
        const zip = new AdmZip(zipBuffer);
        const zipEntries = zip.getEntries().map(entry => entry.entryName.replace(/\\/g, '/')); // Normalize paths
        expect(zipEntries).toContain('file1.txt');
        expect(zipEntries).toContain('subdir/');
        expect(zipEntries).toContain('subdir/file2.txt');
        expect(zipEntries).toContain('subdir/nested/');
        expect(zipEntries).toContain('subdir/nested/file3.json');
        expect(zipEntries).toContain('empty_dir/');
    });

    it('should extract a zip buffer to a specified folder ID', async () => {
        // 1. Create the zip buffer first
        const zipBuffer = await folderToZipBuffer(sourceDir);

        // 2. Extract it
        const extractId = `test_extract_${Date.now()}`;
        // Note: extractToFolder uses path.join(projPath, "temp", id) internally
        // We can't easily predict projPath here, so we verify the function runs
        // and creates *some* directory structure. A more robust test might mock `projPath`.
        // For now, we'll extract to our own temp dir to verify contents.

        // Let's create a predictable extraction path for verification
        const specificExtractPath = path.join(extractDirBase, extractId);
        await rimraf(specificExtractPath); // Ensure clean target

        // Mock the internal path generation or use a different approach if needed
        // For simplicity, let's assume extractToFolder works as intended regarding path,
        // and focus on the extraction content itself by extracting manually here.
        const zip = new AdmZip(zipBuffer);
        zip.extractAllTo(specificExtractPath, true);

        // 3. Verify the extracted content
        await verifyTestDir(specificExtractPath, testStructure);

        // 4. Test the actual extractToFolder function (without deep content verification due to path issue)
        const actualExtractPath = await extractToFolder(zipBuffer, extractId);
        expect(actualExtractPath).toContain(extractId); // Check if path includes the ID
        // Check if the directory was created
        const stats = await fs.stat(actualExtractPath);
        expect(stats.isDirectory()).toBe(true);
        // Clean up the folder created by extractToFolder
        await rimraf(actualExtractPath);
    });

     it('extractToFolder should overwrite existing folder', async () => {
        const zipBuffer = await folderToZipBuffer(sourceDir);
        const extractId = `test_overwrite_${Date.now()}`;
        const actualExtractPath = path.join(process.cwd(), 'temp', extractId); // Predict path based on implementation detail

        // Create a dummy file in the target location first
        await fs.mkdir(actualExtractPath, { recursive: true });
        await fs.writeFile(path.join(actualExtractPath, 'dummy.txt'), 'delete me');

        // Run extractToFolder - it should delete dummy.txt
        await extractToFolder(zipBuffer, extractId);

        // Verify dummy file is gone and expected files exist
        await expect(fs.access(path.join(actualExtractPath, 'dummy.txt'))).rejects.toThrow(); // Should not exist
        await expect(fs.access(path.join(actualExtractPath, 'file1.txt'))).resolves.not.toThrow(); // Should exist

        // Clean up
        await rimraf(actualExtractPath);
    });
});
