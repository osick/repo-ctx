// Extract all type declarations (classes, interfaces, structs) from CPG
//
// Usage: joern --script extract_types.sc --param cpgFile=<cpg.bin> --param outFile=<output.txt>
//
// Output format (pipe-delimited):
// name|fullName|filename|lineStart|inheritsFrom

@main def extract(cpgFile: String, outFile: String) = {
  importCpg(cpgFile)

  cpg.typeDecl.filter(_.isExternal == false).map(t =>
    s"${t.name}|${t.fullName}|${t.filename}|${t.lineNumber.getOrElse(0)}|${t.inheritsFromTypeFullName.mkString(",")}"
  ).l.mkString("\n") #> outFile
}
