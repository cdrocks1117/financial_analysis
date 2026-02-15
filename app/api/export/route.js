import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import ExcelJS from "exceljs";

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function findNumericValue(extractedText, label) {
  if (!extractedText || !label) return "MISSING";

  const lines = extractedText.split(/\r?\n/);
  const labelPattern = new RegExp(escapeRegExp(label), "i");
  const numberRegex = /-?\$?\s*[\d,]+(?:\.\d+)?/g;

  const candidates = new Set();

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) continue;

    if (!labelPattern.test(line)) continue;

    const matches = [...line.matchAll(numberRegex)].map((m) => m[0]);
    for (const match of matches) {
      candidates.add(match.replace(/\$/g, '').replace(/,/g, ''));
    }
  }

  if (candidates.size === 0) {
    return "MISSING";
  }

  if (candidates.size > 1) {
    return "AMBIGUOUS";
  }

  return [...candidates][0];
}

export async function POST(request) {
  try {
    const body = await request.json();
    const { extractedText, mappings } = body || {};

    if (!extractedText || typeof extractedText !== "string") {
      return NextResponse.json(
        { error: "Request body must include 'extractedText' as a string." },
        { status: 400 }
      );
    }

    if (!Array.isArray(mappings)) {
      return NextResponse.json(
        { error: "Request body must include 'mappings' as an array." },
        { status: 400 }
      );
    }

    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet("Financial Mapping");

    // Define columns with proper styling
    sheet.columns = [
      { header: "Original Line Item", key: "original", width: 40 },
      { header: "Standard Line Item", key: "standard", width: 40 },
      { header: "Value (if found)", key: "value", width: 24 },
    ];

    // Style the header row
    sheet.getRow(1).font = { bold: true };
    sheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFE0E0E0' }
    };

    // Add data rows
    let rowNumber = 2;
    mappings.forEach((mapping) => {
      if (!mapping) return;
      const original = typeof mapping.original === "string" ? mapping.original : "";
      const standard = typeof mapping.standard === "string" ? mapping.standard : "";

      if (!original && !standard) return;

      const value = findNumericValue(extractedText, original || standard);

      const row = sheet.addRow({
        original: original || "",
        standard: standard || "",
        value,
      });

      // Color code the value cell based on status
      const valueCell = row.getCell(3);
      if (value === "MISSING") {
        valueCell.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FFFFCCCC' } // Light red
        };
      } else if (value === "AMBIGUOUS") {
        valueCell.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FFFFFFCC' } // Light yellow
        };
      } else {
        valueCell.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FFCCFFCC' } // Light green
        };
      }

      rowNumber++;
    });

    // Add borders to all cells
    sheet.eachRow((row, rowNumber) => {
      row.eachCell((cell) => {
        cell.border = {
          top: { style: 'thin' },
          left: { style: 'thin' },
          bottom: { style: 'thin' },
          right: { style: 'thin' }
        };
      });
    });

    const exportDir = path.join(process.cwd(), "public", "exports");
    await fs.promises.mkdir(exportDir, { recursive: true });

    const filePath = path.join(exportDir, "financial_output.xlsx");

    await workbook.xlsx.writeFile(filePath);

    return NextResponse.json({
      downloadUrl: "/exports/financial_output.xlsx",
    });
  } catch (error) {
    console.error("Error in /api/export:", error);
    return NextResponse.json(
      { error: "Failed to generate Excel export." },
      { status: 500 }
    );
  }
}