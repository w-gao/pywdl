version development

#import "other.wdl" as other

workflow wf_1 {

  input {
    String in_str = "hi"  # bounded
    String? in_str_opt    # optional
    Int in_int            # unbounded
    Array[String] in_arr
    Pair[String, Int] in_pair
  }
	String rev_str = if in_str == "hi" then "bye" else in_str

  call task_1 {input: in_str=in_str}

  Array[Int] scatters = [1, 2, 3, 4, 5]

  scatter ( i in scatters) {
	  call task_2 as bar {input: in_int=i}
  }

  output {
    Array[String] wf_out = bar.out
  }
}

task task_1 {

  input {
    String in_str = "twenty"
  }

  runtime {
    container: "ubuntu:latest"
    cpu: 1
    memory: "3GB"
  }

  command <<<
  >>>

  output {
    String t1_out = ""
  }
}

task task_2 {
  input {
    Int in_int
  }

  command <<<
    echo "out: ~{in_int}"
  >>>

  output {
    String t2_out = read_string(stdout())
  }
}
