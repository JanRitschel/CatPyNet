public class test {
    public static void main(String[] args){
        String catalysts = "[a, b, c * d,   (e f)]";
        catalysts = catalysts.replaceAll("\\|", ",")
        .replaceAll("\\*", "&")
        .replaceAll("\\s*\\(\\s*", "(")
        .replaceAll("\\s*\\)\\s*", ")")
        .replaceAll("\\s*&\\s*", "&")
        .replaceAll("\\s*,\\s*", ",")
        .replaceAll("\\s+", ",");
        System.out.println(catalysts);
    }
    
}
