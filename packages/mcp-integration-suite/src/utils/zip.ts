import { mkdir, writeFile } from "node:fs/promises";
import { logInfo, projPath } from "..";
import AdmZip from "adm-zip";
import path from "node:path";
import { rimraf } from "rimraf";

/**
 * Extracts a ZIP buffer to a specified folder
 * @param zipBuf - The ZIP file as a buffer
 * @param id - The unique identifier for the extraction folder
 * @returns The path to the extracted folder
 */
export const extractToFolder = async (
	zipBuf: Buffer,
	id: string
): Promise<string> => {
	const iflowPath = path.join(projPath, "temp", id);
	await rimraf(iflowPath);
	await mkdir(iflowPath, { recursive: true });

	const zip = new AdmZip(zipBuf);
	zip.extractAllTo(iflowPath, true);

	return iflowPath;
};

/**
 * Converts a folder to a ZIP buffer
 * @param path - The path to the folder to be zipped
 * @returns A buffer containing the zipped folder
 */
export const folderToZipBuffer = async (path: string): Promise<Buffer> => {
	const zip = new AdmZip();
	logInfo(`Adding ${path} to ZIP archive`);
	zip.addLocalFolder(path);
	return zip.toBufferPromise();
};
