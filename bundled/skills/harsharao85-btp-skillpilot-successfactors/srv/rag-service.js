require("dotenv").config();

"use strict";

const express = require("express");
const fs = require("fs");
const path = require("path");
const Anthropic = require("@anthropic-ai/sdk");

const app = express();
app.use(express.json());

// ---------------------------------------------------------------------------
// 1. DATA LOADING
// ---------------------------------------------------------------------------

function parseCSV(filePath) {
  const raw = fs.readFileSync(filePath, "utf8");
  const lines = raw.trim().split("\n");
  const headers = parseCSVLine(lines[0]);
  return lines.slice(1).map((line) => {
    const values = parseCSVLine(line);
    return Object.fromEntries(headers.map((h, i) => [h.trim(), (values[i] || "").trim()]));
  });
}

// Simple CSV parser that handles quoted fields containing commas
function parseCSVLine(line) {
  const result = [];
  let current = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      inQuotes = !inQuotes;
    } else if (ch === "," && !inQuotes) {
      result.push(current);
      current = "";
    } else {
      current += ch;
    }
  }
  result.push(current);
  return result;
}

const DATA_DIR = path.join(__dirname, "../db/data");

function loadAllData() {
  const files = {
    courses: "skillpilot-Courses.csv",
    learningPaths: "skillpilot-LearningPaths.csv",
    certifications: "skillpilot-Certifications.csv",
    skills: "skillpilot-Skills.csv",
  };

  const data = {};
  for (const [key, file] of Object.entries(files)) {
    data[key] = parseCSV(path.join(DATA_DIR, file));
  }
  return data;
}

// ---------------------------------------------------------------------------
// 2. CHUNKING
// ---------------------------------------------------------------------------

function buildChunks(data) {
  const chunks = [];

  for (const course of data.courses) {
    chunks.push({
      id: `course-${course.ID}`,
      type: "Course",
      title: course.title,
      text: `Course: ${course.title}
Skill Area: ${course.skillArea}
Format: ${course.format} | Duration: ${course.duration}
Prerequisites: ${course.prerequisites || "None"}
Description: ${course.description}`,
    });
  }

  for (const lp of data.learningPaths) {
    chunks.push({
      id: `path-${lp.ID}`,
      type: "Learning Path",
      title: lp.title,
      text: `Learning Path: ${lp.title}
Target Role: ${lp.targetRole} | Duration: ${lp.estimatedDuration}
Description: ${lp.description}`,
    });
  }

  for (const cert of data.certifications) {
    chunks.push({
      id: `cert-${cert.ID}`,
      type: "Certification",
      title: cert.title,
      text: `Certification: ${cert.title}
Validity: ${cert.validityPeriod}
Renewal: ${cert.renewalRules}
Description: ${cert.description}`,
    });
  }

  for (const skill of data.skills) {
    chunks.push({
      id: `skill-${skill.ID}`,
      type: "Skill",
      title: skill.name,
      text: `Skill: ${skill.name}
Proficiency Level: ${skill.proficiencyLevel}
Description: ${skill.description}`,
    });
  }

  return chunks;
}

// ---------------------------------------------------------------------------
// 3. TF-IDF VECTOR STORE (in-memory, no external DB)
// ---------------------------------------------------------------------------

function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((t) => t.length > 2);
}

function buildTFIDF(chunks) {
  // Term frequency for each chunk
  const tfVectors = chunks.map((chunk) => {
    const tokens = tokenize(chunk.text);
    const tf = {};
    for (const token of tokens) {
      tf[token] = (tf[token] || 0) + 1;
    }
    // Normalize by document length
    const len = tokens.length;
    for (const token of Object.keys(tf)) {
      tf[token] = tf[token] / len;
    }
    return tf;
  });

  // Document frequency
  const df = {};
  for (const tf of tfVectors) {
    for (const token of Object.keys(tf)) {
      df[token] = (df[token] || 0) + 1;
    }
  }

  const N = chunks.length;

  // TF-IDF vectors
  const tfidfVectors = tfVectors.map((tf) => {
    const tfidf = {};
    for (const [token, tfVal] of Object.entries(tf)) {
      const idf = Math.log((N + 1) / ((df[token] || 0) + 1)) + 1;
      tfidf[token] = tfVal * idf;
    }
    return tfidf;
  });

  return { tfidfVectors, df, N };
}

function queryVector(queryText, df, N) {
  const tokens = tokenize(queryText);
  const tf = {};
  for (const token of tokens) {
    tf[token] = (tf[token] || 0) + 1;
  }
  const len = tokens.length || 1;
  const tfidf = {};
  for (const [token, count] of Object.entries(tf)) {
    const tfVal = count / len;
    const idf = Math.log((N + 1) / ((df[token] || 0) + 1)) + 1;
    tfidf[token] = tfVal * idf;
  }
  return tfidf;
}

function cosineSimilarity(vecA, vecB) {
  const allKeys = new Set([...Object.keys(vecA), ...Object.keys(vecB)]);
  let dot = 0;
  let magA = 0;
  let magB = 0;
  for (const key of allKeys) {
    const a = vecA[key] || 0;
    const b = vecB[key] || 0;
    dot += a * b;
    magA += a * a;
    magB += b * b;
  }
  if (magA === 0 || magB === 0) return 0;
  return dot / (Math.sqrt(magA) * Math.sqrt(magB));
}

function findTopK(queryText, chunks, tfidfVectors, df, N, k = 3) {
  const qVec = queryVector(queryText, df, N);
  const scored = chunks.map((chunk, i) => ({
    chunk,
    score: cosineSimilarity(qVec, tfidfVectors[i]),
  }));
  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, k).filter((s) => s.score > 0);
}

// ---------------------------------------------------------------------------
// 4. PROMPT ASSEMBLY
// ---------------------------------------------------------------------------

function buildPrompt(question, retrievedChunks) {
  const contextBlocks = retrievedChunks
    .map(
      ({ chunk }, i) =>
        `[Source ${i + 1} — ${chunk.type}: ${chunk.title}]\n${chunk.text}`
    )
    .join("\n\n---\n\n");

  return `You are SkillPilot, an AI learning assistant embedded in SAP SuccessFactors Learning. Your role is to help employees, managers, and L&D administrators navigate SAP learning content related to S/4HANA migration, SAP BTP, SuccessFactors HCM, and enterprise change management.

Always answer based on the provided context. If the context does not contain enough information to answer fully, say so clearly rather than guessing.

CONTEXT (retrieved from the SkillPilot knowledge base):
${contextBlocks}

USER QUESTION:
${question}

Provide a clear, actionable answer. Where relevant, mention specific course titles, learning paths, certifications, or skills from the context. Keep your response concise and practical.`;
}

// ---------------------------------------------------------------------------
// 5. STARTUP — BUILD VECTOR STORE
// ---------------------------------------------------------------------------

console.log("SkillPilot RAG Service starting...");

const rawData = loadAllData();
const chunks = buildChunks(rawData);
const { tfidfVectors, df, N } = buildTFIDF(chunks);

console.log(`Vector store ready: ${chunks.length} chunks indexed`);

// ---------------------------------------------------------------------------
// 6. CLAUDE CLIENT
// ---------------------------------------------------------------------------

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
console.log('Anthropic client key check:', process.env.ANTHROPIC_API_KEY ? 'KEY PRESENT' : 'KEY MISSING');

// ---------------------------------------------------------------------------
// 7. API ENDPOINTS
// ---------------------------------------------------------------------------

// Health check
app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    chunksIndexed: chunks.length,
    model: "claude-sonnet-4-20250514",
    timestamp: new Date().toISOString(),
  });
});

// Chat endpoint
app.post("/api/chat", async (req, res) => {
  console.log('KEY AT REQUEST TIME:', process.env.ANTHROPIC_API_KEY ? 'PRESENT' : 'MISSING');

  const { question } = req.body;

  if (!question || typeof question !== "string" || question.trim().length === 0) {
    return res.status(400).json({ error: "Missing or empty 'question' field in request body." });
  }

  try {
    // Retrieve top-3 relevant chunks
    const topChunks = findTopK(question.trim(), chunks, tfidfVectors, df, N, 3);

    if (topChunks.length === 0) {
      return res.json({
        answer:
          "I couldn't find relevant content in the SkillPilot knowledge base for your question. Try asking about S/4HANA migration, SAP BTP, SuccessFactors, certifications, or specific learning paths.",
        sources: [],
      });
    }

    // Build grounded prompt
    const prompt = buildPrompt(question.trim(), topChunks);

    // Call Claude
    const message = await anthropic.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      messages: [{ role: "user", content: prompt }],
    });

    const answer = message.content[0].type === "text" ? message.content[0].text : "";

    // Build source citations
    const sources = topChunks.map(({ chunk, score }) => ({
      id: chunk.id,
      type: chunk.type,
      title: chunk.title,
      relevanceScore: Math.round(score * 100) / 100,
    }));

    return res.json({ answer, sources });
  } catch (err) {
    console.error("Error calling Claude API:", err.message);
    return res.status(500).json({ error: err.message, stack: err.stack, name: err.name });
  }
});

// List available content (useful for browsing/debugging)
app.get("/api/content", (req, res) => {
  res.json({
    courses: rawData.courses.map((c) => ({ id: c.ID, title: c.title, skillArea: c.skillArea })),
    learningPaths: rawData.learningPaths.map((lp) => ({ id: lp.ID, title: lp.title, targetRole: lp.targetRole })),
    certifications: rawData.certifications.map((cert) => ({ id: cert.ID, title: cert.title })),
    skills: rawData.skills.map((s) => ({ id: s.ID, name: s.name, proficiencyLevel: s.proficiencyLevel })),
  });
});

// ---------------------------------------------------------------------------
// 8. START SERVER
// ---------------------------------------------------------------------------

const PORT = process.env.PORT || 4005;
app.listen(PORT, () => {
  console.log(`SkillPilot RAG Service listening on http://localhost:${PORT}`);
  console.log(`  POST http://localhost:${PORT}/api/chat`);
  console.log(`  GET  http://localhost:${PORT}/api/health`);
  console.log(`  GET  http://localhost:${PORT}/api/content`);
});

module.exports = app;
