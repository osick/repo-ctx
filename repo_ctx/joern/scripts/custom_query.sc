// Template for custom CPGQL queries
//
// Usage: joern --script custom_query.sc --param cpgFile=<cpg.bin> --param outFile=<output.txt> --param query="cpg.method.name.l"
//
// Note: For complex queries, it's often easier to create a dedicated script file

@main def execute(cpgFile: String, outFile: String, query: String = "cpg.method.name.l") = {
  importCpg(cpgFile)

  // The query parameter is executed dynamically
  // Default query lists all method names
  val result = query match {
    case "cpg.method.name.l" => cpg.method.name.l
    case "cpg.typeDecl.name.l" => cpg.typeDecl.name.l
    case "cpg.call.name.l" => cpg.call.name.l
    case "cpg.file.name.l" => cpg.file.name.l
    case _ => List(s"Unknown query: $query")
  }

  result.mkString("\n") #> outFile
}
