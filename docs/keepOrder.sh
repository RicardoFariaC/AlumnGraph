#!/bin/sh
cat <<QUitquIT
# This is a shell archive. 
#
# to execute this file, type:   sh keepOrder_archive.sh
# 
# On Linux/UNIX/MacOS(?) systems it is an executable program that will create 
# a subdirectory (named keepOrder) in the currect directory and then 
# install multiple (text) files in that directory.  
# This shell archive and all contents are humanly readable - no binary files.
#
# Windows OS users will have to manually cut this file up and create any files
# that are desired.  Sorry.
#
# To proceed, type "y" at the prompt.
#
QUitquIT
read -p "Type y to proceed " ans
if [ "$ans" != "y" ];then echo "exiting";exit;fi

if [ -d "keepOrder" ];then
    if [ -w "keepOrder" ];then echo "directory keepOrder exists and is writable";
    else echo  "directory keepOrder exists but is NOT writable\nExiting"; exit; fi
else
    mkdir "keepOrder" ;
    if [ -d "keepOrder" ];then
      if [ -w "keepOrder" ];then echo "directory keepOrder has been created and is writable";
      else echo  "directory keepOrder has been created but is NOT writable\nExiting"; exit;
      fi
    fi
fi
echo writing keepOrder/keepOrder.gvpr
cat >keepOrder/keepOrder.gvpr <<'STopstOP'
BEGIN{
  int ErrorCnt=0;
  node_t  aNode;
  graph_t aGraph;
  string estr;
  ////////////////////////////////////////////////////////////////////
  int istrue(string checkme, int rc) {
    checkme = tolower(checkme);
    //print("// checkme: ", checkme);
    if (checkme == "@(1|yes|true)") // ksh syntax
      rc=1;
    else
      rc=0;
    return(rc);
  }
  //////////////////////////////////////////////////////////////////////
  int isfalse(string checkme, int rc) {
    checkme = tolower(checkme);
    //print("// checkme: ", checkme);
    if (checkme == "@(0|no|false)") // ksh syntax
      rc=1;
    else
      rc=0;
    return(rc);
  }
  ///////////////////////////////////////////////////////////////////////////
  void doErrs(string eString) {
    ErrorCnt++;
    printf(2, "Error:: %s\n", eString);
  }
  /////////////////////////////////////////////////////////////////////////////
  graph_t graphTraverse (graph_t thisGraph) {
    node_t dotOrder[], inputOrder[];
    int do=0, io=0;
    ///////  TEMPORARY - TESTING ONLY  /////////////////////////////
    //if ((hasAttr(thisGraph, "rank")) && (thisGraph.rank!=""))
    //  thisGraph.keepOrder="true";
    ///////////////////////////////////////////////////////////////
    //  check if graph rank has value
    if (((hasAttr(thisGraph, "keepOrder")) && (istrue(thisGraph.keepOrder)==1)) && ((hasAttr(thisGraph, "rank")) && (thisGraph.rank!=""))) {
      //print("//  keepOrder - g:  >", thisGraph.name,"<");
      // find all nodes that have this graph as immediate parent
      // build 2 arrays:
      //  - nodes sequenced by input
      //  - nodes sequenced by dot algorithm (order)
      unset(dotOrder);
      unset(inputOrder);
      io=0;
      for (aNode=fstnode(thisGraph); aNode; aNode = nxtnode_sg(thisGraph, aNode)) {
        if (!((hasAttr(aNode, "pos")) && (aNode.pos!=""))) {
          estr=sprintf("All nodes must have pos attribute.\n");
          doErrs(estr);;
          exit(9);
        }
        inputOrder[++io]=aNode;
        dotOrder[(int)aNode.order]=aNode;
        //print("// check: ", aNode.name,"  >",aNode.order,"<  ", io);
      }
      // compare the two sequences
      // need to go in "order" sequence because there may be gaps
      io=0;
      for (dotOrder[do]) {
        io++;
        //if ((dotOrder[do].rank==inputOrder[io].rank) && (dotOrder[do]!=inputOrder[io])){
        if (dotOrder[do]!=inputOrder[io]) {
          print("//  Out of order: ",dotOrder[do],"  ", inputOrder[io]);
          dotOrder[do].newpos=inputOrder[io].pos;
          // will this work?? (erasing node.xlp) ???
          if (hasAttr(dotOrder[do], "xlp"))
            dotOrder[do].xlp="";
        }
      }
    }
    for (aGraph = fstsubg(thisGraph); aGraph; aGraph = nxtsubg(aGraph)) {
      //print ("//  graph:  >", aGraph.name,"<");
      aGraph = graphTraverse(aGraph);
    }
    return thisGraph;
  }
}
//////////////////////////////////////////////////////////////////////
BEG_G{
  //reset traverse
  // for neato, set splines
  if (!(hasAttr($G, "splines") && $G.splines!=""))
    $G.splines="true";
  graphTraverse($G);
}
N{
  edge_t anEdge;
  if ((hasAttr($, "newpos")) && ($.newpos!="")) {
    $.oldpos=$.pos;
    $.pos=$.newpos;
    // later - fix any node xlp value
    for (anEdge = fstedge($); anEdge; anEdge = nxtedge(anEdge, $)) {
      anEdge.pos="";  // need to recreate these edges
      // later, remove label pos & xlabel pos (xlp)
      if (hasAttr(anEdge, "lp"))
        anEdge.lp="";
      if (hasAttr(anEdge, "xlp"))
        anEdge.xlp="";
    }
  }
}
STopstOP
echo writing keepOrder/keepOrder.README
cat >keepOrder/keepOrder.README <<'STopstOP'

keepOrder.gvpr is a GVPR program that can be used to rearrange nodes within a Graphviz (DOT) graph.  Specifically, keepOrder.gvpr will make sure that all nodes within a subgraph will be displayed in the order that they were defined, as long as that subgraph has two attributes:
- rank must be set to any of the legal values defined by Graphviz (https://graphviz.org/docs/attrs/rank/)
- a new attribute keepOrder must be set to true.  Note that if keepOrder is set at the Root graph-level, it will be inherited by all subgraphs.


below is a command line to run the keepOrder program:

dot -GkeepOrder=true -Gphase=2 myfile.gv | dot -Gphase="" | gvpr -cf keepOrder.gvpr | neato -Gsplines=true -n2 -Tpng  >out.png

Note:
 -Gphase=true can be on the command line or added to your input
  likewise,
 -GkeepOrder=true can be invoked within the input
   at the Root-level
    or
   at the graph-level (not the cluster-level)

setting the phase attribute to 2 will cause dot to calculate all the
  ranks and the "order" of the nodes within each rank and annotate the file
  with that added info


[GVPR (https://www.graphviz.org/pdf/gvpr.1.pdf) is one of the Graphviz programs, just like DOT.]

STopstOP
