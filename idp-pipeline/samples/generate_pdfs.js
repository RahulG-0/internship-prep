const fs = require("fs");
const path = require("path");

const outDir = __dirname;

function escapePdfText(value) {
  return String(value).replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
}

function makePdf(lines, filename) {
  const contentLines = ["BT", "/F1 10 Tf", "14 TL", "50 800 Td"];

  lines.forEach((line, index) => {
    if (index > 0) contentLines.push("T*");
    contentLines.push(`(${escapePdfText(line)}) Tj`);
  });

  contentLines.push("ET");
  const stream = contentLines.join("\n");

  const objects = [
    "<< /Type /Catalog /Pages 2 0 R >>",
    "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    `<< /Length ${Buffer.byteLength(stream, "utf8")} >>\nstream\n${stream}\nendstream`,
  ];

  let pdf = "%PDF-1.4\n";
  const offsets = [0];

  objects.forEach((object, index) => {
    offsets.push(Buffer.byteLength(pdf, "utf8"));
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });

  const xrefOffset = Buffer.byteLength(pdf, "utf8");
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += "0000000000 65535 f \n";
  offsets.slice(1).forEach((offset) => {
    pdf += `${String(offset).padStart(10, "0")} 00000 n \n`;
  });
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\n`;
  pdf += `startxref\n${xrefOffset}\n%%EOF\n`;

  fs.writeFileSync(path.join(outDir, filename), pdf);
  console.log(`Generated ${filename}`);
}

const samples = {
  "invoice_pass.pdf": [
    "DOCUMENT TYPE: INVOICE - RULE PASS SAMPLE",
    "Invoice Number: INV-PASS-001",
    "Invoice Date: 2026-05-01",
    "Due Date: 2026-06-30",
    "Vendor Name: Northstar Office Supplies Inc.",
    "Vendor Address: 100 King Street West, Toronto ON",
    "Vendor Email: billing@northstar.example",
    "Bill To Name: TD Bank Group",
    "Bill To Address: 66 Wellington Street West, Toronto ON",
    "PO Number: PO-2026-100",
    "Currency: CAD",
    "Line Item: Printer paper, Quantity 10, Unit Price 25.00, Line Total 250.00",
    "Line Item: Toner cartridges, Quantity 4, Unit Price 150.00, Line Total 600.00",
    "Subtotal: 850.00",
    "Tax Rate: 0.13",
    "Tax Amount: 110.50",
    "Discount Amount: 0.00",
    "Total Amount: 960.50",
    "Expected result: approved. Line items match subtotal, due date is not overdue, total is below approval threshold.",
  ],
  "invoice_fail.pdf": [
    "DOCUMENT TYPE: INVOICE - RULE FAIL SAMPLE",
    "Invoice Number: INV-FAIL-001",
    "Invoice Date: 2026-01-01",
    "Due Date: 2026-01-15",
    "Vendor Name: Apex Systems Consulting",
    "Vendor Address: 500 Queen Street West, Toronto ON",
    "Vendor Email: ar@apexsystems.example",
    "Bill To Name: TD Bank Group",
    "Bill To Address: 66 Wellington Street West, Toronto ON",
    "PO Number: PO-2026-999",
    "Currency: CAD",
    "Line Item: Enterprise implementation, Quantity 1, Unit Price 9000.00, Line Total 9000.00",
    "Line Item: Support retainer, Quantity 1, Unit Price 2000.00, Line Total 2000.00",
    "Subtotal: 12000.00",
    "Tax Rate: 0.13",
    "Tax Amount: 1560.00",
    "Discount Amount: 0.00",
    "Total Amount: 13560.00",
    "Expected result: needs review. Line items do not match subtotal, due date is overdue, total exceeds approval threshold.",
  ],
  "bank_statement_pass.pdf": [
    "DOCUMENT TYPE: BANK STATEMENT - RULE PASS SAMPLE",
    "Bank Name: TD Bank",
    "Account Holder Name: Priya Shah",
    "Account Number: 1234 5678 9012 4321",
    "Account Type: chequing",
    "Statement Start Date: 2026-04-01",
    "Statement End Date: 2026-04-30",
    "Currency: CAD",
    "Opening Balance: 5000.00",
    "Total Credits: 2500.00",
    "Total Debits: 1800.00",
    "Closing Balance: 5700.00",
    "Transaction: 2026-04-03, Payroll Deposit, credit, Amount 2500.00, Running Balance 7500.00",
    "Transaction: 2026-04-10, Rent Payment, debit, Amount 1500.00, Running Balance 6000.00",
    "Transaction: 2026-04-18, Grocery Store, debit, Amount 300.00, Running Balance 5700.00",
    "Expected result: approved. Balances reconcile and transaction dates are sequential.",
  ],
  "bank_statement_fail.pdf": [
    "DOCUMENT TYPE: BANK STATEMENT - RULE FAIL SAMPLE",
    "Bank Name: TD Bank",
    "Account Holder Name: Marcus Lee",
    "Account Number: 5555 6666 7777 8888",
    "Account Type: savings",
    "Statement Start Date: 2026-04-01",
    "Statement End Date: 2026-04-30",
    "Currency: CAD",
    "Opening Balance: 5000.00",
    "Total Credits: 1000.00",
    "Total Debits: 700.00",
    "Closing Balance: 4900.00",
    "Transaction: 2026-04-20, Wire Transfer, debit, Amount 15000.00, Running Balance -10000.00",
    "Transaction: 2026-04-05, Payroll Deposit, credit, Amount 1000.00, Running Balance 6000.00",
    "Expected result: needs review. Closing balance does not reconcile, includes a large transaction, and dates are not sequential.",
  ],
  "loan_application_pass.pdf": [
    "DOCUMENT TYPE: LOAN APPLICATION - RULE PASS SAMPLE",
    "Full Name: Emily Carter",
    "Date of Birth: 1992-08-14",
    "SIN: 999 888 321",
    "Address: 25 Bay Street, Toronto ON",
    "Phone: 416-555-0199",
    "Email: emily.carter@example.com",
    "Employment Status: employed",
    "Employer Name: Maple Analytics",
    "Job Title: Senior Analyst",
    "Years Employed: 5",
    "Annual Income: 96000.00",
    "Loan Amount Requested: 18000.00",
    "Loan Purpose: home renovation",
    "Loan Term Months: 60",
    "Collateral: none",
    "Monthly Expenses: 2400.00",
    "Existing Monthly Debt: 800.00",
    "Self Reported Credit Score: 742",
    "Number Of Dependents: 1",
    "Has Co Applicant: false",
    "Expected result: approved. Applicant is adult, DTI is below threshold, required fields are present, and income supports the loan.",
  ],
  "loan_application_fail.pdf": [
    "DOCUMENT TYPE: LOAN APPLICATION - RULE FAIL SAMPLE",
    "Full Name: Jordan Miller",
    "Date of Birth: 2010-02-10",
    "SIN: 111 222 333",
    "Address: 90 Front Street, Toronto ON",
    "Phone: 416-555-0101",
    "Email: jordan.miller@example.com",
    "Employment Status: part-time",
    "Employer Name: Weekend Retail",
    "Job Title: Associate",
    "Years Employed: 0.5",
    "Annual Income: 18000.00",
    "Loan Amount Requested: 30000.00",
    "Loan Purpose: vehicle purchase",
    "Loan Term Months: 24",
    "Collateral: none",
    "Monthly Expenses: 1600.00",
    "Existing Monthly Debt: 1200.00",
    "Self Reported Credit Score: 590",
    "Number Of Dependents: 0",
    "Has Co Applicant: false",
    "Expected result: needs review. Applicant is under 18, DTI exceeds threshold, and income does not support the requested loan.",
  ],
};

Object.entries(samples).forEach(([filename, lines]) => makePdf(lines, filename));
