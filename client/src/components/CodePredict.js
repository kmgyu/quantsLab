import React, { Component } from 'react';

class CodePredict extends Component {
    constructor(props) {
        super(props);
        this.state = {
            data: null,
            loading: false,
        };
    }

    componentDidUpdate(prevProps) {
        if (prevProps.code !== this.props.code) {
            this.setState({ loading: true });

            let api_url = "http://127.0.0.1:5000/codes/" + this.props.code + "/predict";
            fetch(api_url)
                .then(res => res.json())
                .then(data => {
                    this.setState({ data: data["message"], loading: false });
                });
        }
    }

    render() {
        console.log("CodePredict render", this.state.data);

        return (
            <div>
                {this.state.loading ? (
                    <p>Loading...</p>
                ) : (
                    this.state.data !== null ? (
                        this.state.data === "up" ? (
                            <p>다음날 주가가 상승할 것으로 예측됩니다.</p>
                        ) : (
                            <p>다음날 종가가 하락할 것으로 예측됩니다.</p>
                        )
                    ) : (
                        null
                    )
                )}
            </div>
        );
    }
}

export default CodePredict;