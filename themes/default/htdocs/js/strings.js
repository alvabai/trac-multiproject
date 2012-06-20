/*                                                          */
/* Functions for stripping unwanted characters from strings */
/*                                                          */
function stripAll(str, specials) {
  var fstr = "";
  var html = 0;
  var newl = true;
  // strip html code and special characters if selected
  for (i=0;i < str.length ; i++) {
    switch(str[i]) {
      case '<':
         html += 1;
         break;
      case '>':
         if (html>0) html -= 1;
         break
      case 0: case '\r': case '\t': case '\v': case '\"': case '\'':
         break;
      case '\n':
         if (newl == false) fstr += str[i];
         newl = true;
         break;
      case '.': case ',': case '+': case '?': case '!': case '/': case '%':
      case '[': case ']': case '(': case ')': case '{': case '}': case '*':
      case '#': case ';': case ':': case '=': case '\\': 
         if (html == 0 && specials) {
           fstr += str.substring(i,i+1);
           newl = false;
         }
         break;
      default:
         if (html == 0) {
           fstr += str.substring(i,i+1);
           newl = false;
         } 
         break;
    }
  }
  // strip leading spaces
  fstr = fstr.replace( /^\s+/g, "" );
  // strip trailing spaces
  fstr = fstr.replace( /\s+$/g, "" );
  return fstr;
}
