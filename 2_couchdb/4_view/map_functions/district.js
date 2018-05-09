//group 25
//* Youshao Xiao - 876548
//* Jiaheng Zhu - 848432
//* Lina Zhou - 941539
//* Haimei Liu - 895804
//* Miaomiao Zhang - 895216

// Map function to find  position of tweets
// _count will be used as a reduce function
// group_level = 1 for the number of tweets on each state
// group_level = 2 for the number of tweets on each district in Victoria
// group_level = 3 for the number of tweets on each district in Melbourne


function(doc) {

  emit([doc.state,doc.districtInVic,doc.districInMel], 1);


}
