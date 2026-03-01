// Extract all methods/functions from CPG
//
// Usage: joern --script extract_methods.sc --param cpgFile=<cpg.bin> --param outFile=<output.txt>
//
// Output format (pipe-delimited):
// name|fullName|filename|lineStart|lineEnd|signature|parameters

@main def extract(cpgFile: String, outFile: String) = {
  importCpg(cpgFile)

  cpg.method.filter(_.isExternal == false).map(m =>
    s"${m.name}|${m.fullName}|${m.filename}|${m.lineNumber.getOrElse(0)}|${m.lineNumberEnd.getOrElse(0)}|${m.signature}|${m.parameter.map(p => p.name + ":" + p.typeFullName).mkString(";")}"
  ).l.mkString("\n") #> outFile
}
