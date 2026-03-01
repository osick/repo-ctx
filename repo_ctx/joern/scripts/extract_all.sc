// Combined extraction script for repo-ctx
// Extracts methods, types, members, and calls in a single pass
//
// Usage: joern --script extract_all.sc --param cpgFile=<cpg.bin> --param outFile=<output.txt>

@main def extract(cpgFile: String, outFile: String) = {
  importCpg(cpgFile)

  val methods = cpg.method.filter(_.isExternal == false).map(m =>
    s"METHOD|${m.name}|${m.fullName}|${m.filename}|${m.lineNumber.getOrElse(0)}|${m.lineNumberEnd.getOrElse(0)}|${m.signature}|${m.parameter.map(p => p.name + ":" + p.typeFullName).mkString(";")}"
  ).l

  val types = cpg.typeDecl.filter(_.isExternal == false).map(t =>
    s"TYPE|${t.name}|${t.fullName}|${t.filename}|${t.lineNumber.getOrElse(0)}|${t.inheritsFromTypeFullName.mkString(";")}"
  ).l

  val members = cpg.member.map(m =>
    s"MEMBER|${m.name}|${m.typeFullName}|${m.typeDecl.fullName.headOption.getOrElse("")}"
  ).l

  val calls = cpg.call.filter(c => c.method.isExternal == false).map(c =>
    s"CALL|${c.method.name.headOption.getOrElse("")}|${c.name}|${c.lineNumber.getOrElse(0)}"
  ).l

  (methods ++ types ++ members ++ calls).mkString("\n") #> outFile
}
