import { z } from 'zod';

export const sendRequestSchema = {
    path: z.string().describe("HTTP Path to send the request to"),
    method: z
        .union([
            z.literal("GET"),
            z.literal("POST"),
            z.literal("PUT"),
            z.literal("DELETE"),
        ])
        .default('POST')
        .describe("HTTP Method to use"),
    body: z.string().optional().describe("request body"),
    headers: z
        .array(
            z.object({
                key: z.string().describe("header"),
                value: z.string().describe("Header Value"),
            })
        )
        .optional()
        .describe("Additional Request headers in key/value format"),
    contentType: z.string().default('application/json').describe('Content type used in header. Defaults to application/json'),
};

export const messageFilterSchema = z
.object({
    LogStart: z
        .string()
        .optional()
        .describe(
            "Starting date/time of selection in format 2017-04-13T15:51:04"
        ),
    LogEnd: z
        .string()
        .optional()
        .describe(
            "End of selection of messages in format 2017-04-13T15:51:04"
        ),
    integrationFlowId: z
        .string()
        .optional()
        .describe("Filter by messages from one Iflow only"),

    // TODO: make union for available statuses
    status: z
        .array(
            z.union([
                z.literal("INFO"),
                z.literal("RETRY"),
                z.literal("FAILED"),
                z.literal("ABANDONED"),
                z.literal("COMPLETED"),
                z.literal("PROCESSING"),
                z.literal("ESCALATED"),
                z.literal("DISCARDED"),
            ])
        )
        .optional()
        .describe("filter by message statuses"),
    sender: z.string().optional().describe("Filter by message sender"),
    receiver: z.string().optional().describe("Filter by message receiver"),
    msgGUID: z.string().optional().describe("Unique message ID"),
    
})
.describe("available filtering options");
