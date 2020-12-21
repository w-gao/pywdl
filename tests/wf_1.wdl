# this is a valid WDL workflow but does not execute on Toil, unfortunately.

version development

#import "other.wdl" as other

workflow wf_1 {
  input {
    String in_str = "hi"  # bounded
    String? in_str_opt    # optional
    Int in_int            # unbounded
    Boolean in_bool = true
    Array[String] in_arr
    Pair[String, Int] in_pair
  }

	String ternary_str = if in_int > 19 then "yes!" else "no :("

  if (in_bool) {
    # conditionals
  }
  if (in_bool) {
    String temp = "Test"
  }
  # temp should be set to None if not defined!

  call t1 {input: in_str=temp}

  Array[Int] scatters = [1, 2, 3, 4, 5]

  scatter ( i in scatters) {
	  call t2 as bar
  }

  output {
    Array[Int] wf_out = bar.num
  }
}

task t1 {

  input {
    String? in_str
    Int in_int = 20
    Float in_float = 3.14
  }

  String non_input_str = "yes"

  command <<<
  >>>
}

task t2 {
  command {}

  output {
    Int num = 3  # seems like Toil parses this to string '3', which is werid.
  }
}

task t3 {
  command {
    echo "line 1"
    echo "line 2"
    echo "line 3"
  }

  runtime {
    container: "ubuntu:latest"
    cpu: 1
    memory: "3GB"
  }

  output {}
}

task t4 {
  String var1 = "hello"
  String var2 = "hello"
  Float num = 1.9
  command {
    echo ~{var1} ~{var2} > output_file.txt
  }
}
