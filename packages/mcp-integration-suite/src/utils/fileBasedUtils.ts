import { promises as fs } from "fs";
import { glob } from "glob";
import path from "path";
import { logInfo } from "..";
import { appendFile, mkdir, writeFile } from "fs/promises";

/**
 * Get all files of a folder as one concatinated string for AI readability
 * @param folderPath Path to the folder to parse
 * @returns All files of folder as text in a single string in Format <relative Path>\n---begin-of-file---\n<file content>\n---end-of-file---\n\
 */
export const parseFolder = async (folderPath: string): Promise<string> => {
	const allFiles = await glob(path.join(folderPath, "**", "*").replace(/\\/g, '/'), { nodir: true });

	let resultString = "";

	for (const file of allFiles) {
		resultString += file + "\n---begin-of-file---\n";
		resultString += await fs.readFile(file, "utf-8");
		resultString += "\n---end-of-file---\n\n";
	}

	logInfo(
		`Done parsing ${folderPath} Total length is  ${resultString.length}`
	);

	return resultString;
};

/**
 * Replace a file in a folder
 * @param basePath Path of the project 
 * @param relativePath relativ Path within the project
 * @param content that should be written to the file
 * @returns 
 */
export const patchFile = async (
	basePath: string,
	relativePath: string,
	content: string,
	append: boolean
): Promise<void> => {
	const filePath = path.join(basePath, relativePath);

	if (append) {
		await appendFile(filePath, content);
	}

	await mkdir(path.dirname(filePath), { recursive: true });
	await writeFile(filePath, content);
	return;
};