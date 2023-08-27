export function extractSentenceAroundKeyword(sentence, keyword) {
    const regex = new RegExp(`"([^"]*${keyword}[^"]*)"`, 'gi');
    const match = sentence.match(regex);

    if (match) {
      return match[0].substring(1, match[0].length - 1);
    } else {
      return null;
    }
}
