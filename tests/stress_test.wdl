version development

workflow stress_test {

  input {
    Int n0 = 0
    Int n1 = 1
    Int n2 = 2
    Int n3 = 3
    Int n4 = 4
    Int n5 = 5
    Int n6 = 6
    Int n7 = 7
    Int n8 = 8
  }

  # TODO: update to more complecated expressions

  Boolean b0 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b1 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b2 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b3 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b4 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b5 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b6 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b7 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b8 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b9 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b10 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b11 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b12 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b13 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b14 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
  Boolean b15 = n0 && n1 || n2 && (n3 || n4) && (n5 || n6) && (n7 || n8) && 10
}
