import path from "path";
import { projPath } from "../..";

const resourceBasePath = path.resolve(projPath, "./resources/examples/mappings/");


export const availableExamples: {
    [name: string]: { description: string; _path: string };
} = {
    mm_material_clasification: {
        description: "Complex mapping using Message Mapping + Scripts. It converts to a CLFMAS02. Its business context is SAP ERP material clasification",
        _path: path.join(resourceBasePath, "mm_material_clasification")
    },
    mm_material_management: {
        description: "Complex mapping using Message Mapping + Scripts. It converts to. It converts to a COND_A01. Its business context is SAP ERP material clasification",
        _path: path.join(resourceBasePath, "mm_material_management")
    },
    mm_pricing_conditions: {
        description: "Complex mapping using Message Mapping + Scripts. It is used for SAP SD pricing conditions",
        _path: path.join(resourceBasePath, "mm_pricing_conditions")
    },
    mm_simple_1_to_1: {
        description: "Simple direct mapping between similar structures",
        _path: path.join(resourceBasePath, "mm_simple_1_to_1")
    }
};