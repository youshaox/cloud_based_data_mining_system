// Map function to find using frequency of each emoji_expression

// _count will be used as a  reduce function
// group_level = 2 for counting the times of each expression on each state


function (doc) {
  if (doc.emoji_list !== null){
  emit([doc.state,doc.emoji_list], 1);
  }
}