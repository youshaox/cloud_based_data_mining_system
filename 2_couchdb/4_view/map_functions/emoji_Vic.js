//group 25
//* Youshao Xiao - 876548
//* Jiaheng Zhu - 848432
//* Lina Zhou - 941539
//* Haimei Liu - 895804
//* Miaomiao Zhang - 895216

// Map function to find using frequency of each emoji_expression

// _count will be used as a  reduce function
// group_level = 2 for counting the times of each expression on each district in Victoria

function (doc) {

  if (doc.state==="VICTORIA" && doc.districtInVic!==null && doc.emoji_list!==null) {
      emit([doc.districtInVic, doc.emoji_list], 1);
  }
}

