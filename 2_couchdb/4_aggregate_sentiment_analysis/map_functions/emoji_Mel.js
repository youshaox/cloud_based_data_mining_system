// Map function to find using frequency of each emoji_expression

// _count will be used as a  reduce function
// group_level = 2 for counting the times of each expression on each district in Melbourne

function (doc) {

  if (doc.state==="VICTORIA" && doc.districtInVic==="MELBOURNE" && doc.districtInMe !==null  && doc.emoji_list!==null) {
      emit([doc.districtInMel, doc.emoji_list], 1);
  }
}
