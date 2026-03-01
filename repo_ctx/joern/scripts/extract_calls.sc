// Extract call graph from CPG
//
// Usage: joern --script extract_calls.sc --param cpgFile=<cpg.bin> --param outFile=<output.txt>
//
// Output format (pipe-delimited):
// callerMethod|calledFunction|lineNumber

@main def extract(cpgFile: String, outFile: String) = {
  importCpg(cpgFile)

  cpg.call.filter(c => c.method.isExternal == false).map(c =>
    s"${c.method.name.headOption.getOrElse("")}|${c.name}|${c.lineNumber.getOrElse(0)}"
  ).l.mkString("\n") #> outFile
}
