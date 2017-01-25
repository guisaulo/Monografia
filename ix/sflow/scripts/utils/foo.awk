BEGIN {                # The BEGIN block is executed before the files are read
    FS="[;]"          # Set the FS to be either a comma or semi-colon
    OFS="."            # Set the OFS (output field separator) to be a comma
}


NR == FNR {
  rep[$1] = $2
  next
} 

{
    for (key in rep) {
      gsub(key, rep[key])
    }
    print
}
