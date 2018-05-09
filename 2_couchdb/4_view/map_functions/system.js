//group 25
//* Youshao Xiao - 876548
//* Jiaheng Zhu - 848432
//* Lina Zhou - 941539
//* Haimei Liu - 895804
//* Miaomiao Zhang - 895216

//Map function to find the the distribution of phone system on each state
// _count as reduce function
//group_level = 2 for the number of each system on each state


function(doc) {
  if(doc.system !== null){
    emit([doc.state,doc.system], 1);
  }
}
