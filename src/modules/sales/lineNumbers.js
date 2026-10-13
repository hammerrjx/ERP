export function previewLineNumbers(lines, savedLines = []) {
  let next = Math.max(0, ...savedLines.map((line) => Number(line.line_number) || 0),
    ...lines.filter((line) => line.id).map((line) => Number(line.line_number) || 0))
  return lines.map((line) => line.id ? line.line_number : (next += 10))
}
