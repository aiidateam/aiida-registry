/** 
* Find the sentence where the search query mentioned.
* @param {string} matchedEntryPoint Entry point data dumped as string.
* @param {string} keyword search query.
* @returns {Array} List of three strings, before matched word, matched word, and after matched word.
*/
export function extractSentenceAroundKeyword(matchedEntryPoint, keyword) {
    const jsonObject = JSON.parse(matchedEntryPoint);
    let matchingSentences = [];

    //Recursively loop through the object until finding a string value.
    function processKeyValuePairs(key, value) {
        if (typeof value === "string" && value.toLowerCase().includes(keyword.toLowerCase())) {
            return value.trim();

        } else if (typeof value === "object") {
            for (const innerKey in value) {
                const processedValue = processKeyValuePairs(innerKey, value[innerKey]);
                //If the string is part of an array (innerKey is a number),
                //get the previous or next line to add more context.
                if (innerKey > 0 && typeof processedValue == 'string') {
                    matchingSentences.push(key + ': ' + value[(innerKey - '1').toString()] + ' ' + processedValue);
                } else if (innerKey == 0 && value.length > 1 && typeof processedValue == 'string') {
                    matchingSentences.push(key + ': ' + processedValue + ' ' + value['1']);
                } else if (typeof processedValue == 'string') {
                    matchingSentences.push(innerKey + ': ' + processedValue);
                }
            }
        }
    }

    for (const key in jsonObject) {
        processKeyValuePairs(key, jsonObject[key]);
    }

    //The matchingSentences array now contains a list of matching sentences.
    //We display only the first matching sentence in the list.
    const matchingSentence = matchingSentences[0];
    let contextArray = [];
    try {
        const lowercaseMatchingSentence = matchingSentence.toLowerCase();
        const lowercaseKeyword = keyword.toLowerCase();

        const indexOfKeyword = lowercaseMatchingSentence.indexOf(lowercaseKeyword);

        //This splitting helps in highlighting the keyword.
        if (indexOfKeyword !== -1) {
          const beforeKeyword = matchingSentence.substring(0, indexOfKeyword);
          const keyword = matchingSentence.substring(indexOfKeyword, indexOfKeyword + lowercaseKeyword.length);
          const afterKeyword = matchingSentence.substring(indexOfKeyword + lowercaseKeyword.length);

          contextArray = [beforeKeyword, keyword, afterKeyword];
    }
    } catch (error) {
        contextArray = [null, null, null];
    }

    return contextArray
}
