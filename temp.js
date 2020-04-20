const dbUtils = {
    processSortValue(sort) {
        const sortFixed = sort.replace('id', '_id');
        const sortSplit = sort.split(' ');
        if (sortSplit.length > 1) {
            // const temp = [];
            // sortSplit.forEach(s => {
            //     temp.push(s);
            // })
            // return temp;
            return [...sortSplit]
        } else 
            return sortFixed;
    }
}
const result = dbUtils.processSortValue('updated text');
console.log(result)