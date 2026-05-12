public class PalindromeChecker {
    public static boolean isPalindrome(String str) {
        String cleanStr = str.toLowerCase().replaceAll("[^a-z0-9]", "");
        int left = 0;
        int right = cleanStr.length() - 1;
        
        while (left < right) {
            if (cleanStr.charAt(left) != cleanStr.charAt(right)) {
                return false;
            }
            left++;
            right--;
        }
        return true;
    }

    public static void main(String[] args) {
        String input = "A man, a plan, a canal, Panama";
        if (isPalindrome(input)) {
            System.out.println("The input is a palindrome.");
        } else {
            System.out.println("The input is not a palindrome.");
        }
    }
}
