import path from "path";
import { projPath } from "../../..";
import { convertAll } from "./bpmnLib";
import { glob } from "glob";
import { mkdtemp, readFile, rm } from "fs/promises";
// returns base64 image png
export const getiFlowToImage = async (iflowPath: string): Promise<string> => {
	const iflowXmPath = (await glob(iflowPath.replace(/\\/g, '/') + "/**/*.iflw"))[0];

	if (!iflowXmPath) {
		throw new Error("Could not locate iflow XML");
	}

	const tempPngPath = path.join(
		await mkdtemp(path.join(projPath, "temp", "file")),
		"output.png"
	);

	await convertAll(
		[
			{
				input: iflowXmPath,
				outputs: [tempPngPath],
			},
		],
		{
			minDimensions: { width: 1200, height: 800 },
			deviceScaleFactor: 2,
		}
	);


    const encodedPngStr = await readFile(tempPngPath, {encoding: 'base64'});
    await rm(tempPngPath);
	return encodedPngStr;
};
