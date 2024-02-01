import React, { Component } from 'react';

class OrderList extends Component{
    constructor(props){
        super(props);
        this.state = { 
            orderList : []
        };
    }
    componentDidMount(){
        console.log("OrderList componentDidMount");
        let api_url = "http://127.0.0.1:5000/orders";
        let options = [];
        fetch(api_url)
            .then(res => res.json())
            .then(data =>{
                console.log("didmount fetch", data);
                this.setState({orderList:data});
            });
    }

    render(){
        return  (
            <div>
                {this.state.orderList.map(item=>{
                    return (<div key={item["order_no"]}>
                        ${item["order_no"]} : {item["st_quantity"]} <br/>
                        {item["code"]}, {item["status"]}
                        </div>);
                })
                }
            </div>
         );
    }
}

export default OrderList;