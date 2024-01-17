// https://observablehq.com/@harrylove/draw-lines-between-circles-nodes-using-d3-links

async function check_all_set() {
    const response = await fetch("/games/1/player/2/network");
    const data = await response.json();
    const width = 1000
    const height = 400
    const offset = 175
    const v_offset = 50

    const svg = d3.select('#network')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    let nodes = [];
    nodes.push([offset, v_offset]); // 1
    nodes.push([offset, height - v_offset]); // 2
    nodes.push([(width) / 3, height/ 2]); // 3
    nodes.push([2 * (width) / 3, height / 2 ]); // 4 
    nodes.push([width - offset,  v_offset]); // 5
    nodes.push([width - offset, (height - v_offset) ]); // 6

    

    let links = [];

    links.push(
        d3.linkHorizontal()({
        source: nodes[0],
        target: nodes[2]
        })
    );

    links.push(
        d3.linkHorizontal()({
            source: nodes[1],
            target: nodes[2]
        })
    );

    links.push(
        d3.linkHorizontal()({
            source: nodes[2],
            target: nodes[3]
        })
    );

    links.push(
    d3.linkHorizontal()({
        source: nodes[3],
        target: nodes[4]
    })
    );

    links.push(
    d3.linkHorizontal()({
        source: nodes[3],
        target: nodes[5]
    })
    );

    if (data.is_integrated) {
        // integrated
        links.push(
            d3.linkHorizontal()({
            source: nodes[1],
            target: nodes[5]
            })
        );
        links.push(
            d3.linkHorizontal()({
            source: nodes[0],
            target: nodes[4]
            })
        );  
    } else {
        // segregated
        links.push(
            d3.linkHorizontal()({
            source: nodes[0],
            target: nodes[1]
            })
        );
        
        links.push(
            d3.linkHorizontal()({
            source: nodes[4],
            target: nodes[5]
            })
        );
    }

    for (let i = 0; i < links.length; i++) {
        svg
            .append('path')
            .attr('d', links[i])
            .attr('stroke', 'white')
            .attr('stroke-width', 3)
            .attr('fill', 'none');
    }

    data.data.forEach(element => {
        i = element['position'] - 1
        element['cx'] = nodes[i][0]
        element['cy'] = nodes[i][1]
    });

    console.log(data.data)

    const Tooltip = d3.select("#network")
      .append("div")
      .attr("class", "tooltip")
      .style("opacity", 0)
      .style("background-color", "white")
      .style("border", "solid")
      .style("border-width", "2px")
      .style("border-radius", "1px")
      .style("padding", "5px")

    // Three function that change the tooltip when user hover / move / leave a cell
    const mouseover = function(event, d) {
      Tooltip.style("opacity", 1)
    }
    var mousemove = function(event, d) {
      Tooltip
        .html(d.name + "<br>" )
        .style('font', "16pt sans-serif")
        .style('color', "black")
        .style("left", (event.x) + "px")
        .style("top", (event.y) - 30 + "px")
    }
    var mouseleave = function(event, d) {
      Tooltip.style("opacity", 0)
    }


    svg.selectAll('g')
        .data(data.data)
        .join('circle')
        .attr('r', 40)
        .attr('cx', function(d){
            return d.cx
        })
        .attr('cy', function(d){
            return d.cy
        })
        .style('fill', function(d){
            if (d.this_player) {
                return "lightgreen"
            } else {
                return "grey"
            }
        })
        .on("mouseover", mouseover)
      .on("mousemove", mousemove)
      .on("mouseleave", mouseleave)

    // svg.selectAll('g')
    //     .data(data.data)
    //     .join('text')
    //     .text(function(d){
    //         return d.name
    //     })
    //     .attr('x', function(d){
    //         return d.cx
    //     })
    //     .attr('y', function(d){
    //         return d.cy - 20
    //     })
    //     .style('font', "16pt sans-serif")
    //     .style('fill', "white")
    //     .style('opacity', 1)
    //     .on("mouseover", function(e,d) {
    //         console.log(d3.pointer(e))
    //         d3.select(this).style("opacity", 1)
    //         })
    //         .on("mouseout", function(e, d) {
    //             d3.select(this).style("opacity", 0)
    //         })


    // for (let i = 0; i < nodes.length; i++) {
    //     let g = svg.append('g')
        
            
    //     g.append('circle')
    //     .attr('cx', nodes[i][0])
    //     .attr('cy', nodes[i][1])
    //     .attr('r', 40)
    //     .style('fill', function(){
    //         if (data.data[i].this_player) {
    //             return "lightgreen"
    //         } else {
    //             return "grey"
    //         }
    //     })
        

    //     g.append('text')
    //     .attr('x', nodes[i][0])
    //     .attr('y', nodes[i][1] - 20)
        // .style('font', "16pt sans-serif")
        // .style('fill', "white")
        // .style('opacity', 1)
        // .text(data.data[i].name)
        // .on("mouseover", function(e,d) {
        //     console.log(d3.pointer(e))
        //     d3.select(this).style("opacity", 1)
        //     })
        //     .on("mouseout", function(e, d) {
        //         d3.select(this).style("opacity", 0)
        //     })
    // }



}

$(document).ready( function () {
    check_all_set();
  });