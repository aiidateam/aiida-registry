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

    let extractedSentence = [];
    try {
        extractedSentence = matchingSentences[0].split(keyword.toLowerCase());
    } catch (error) {
        extractedSentence = [null, null];
    }

    return extractedSentence;
}
