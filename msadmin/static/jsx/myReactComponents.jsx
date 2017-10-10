

// var MyTextfield = React.createClass({
//     render: function() {
//         return <input type='text' />;
//     }
// });

// class MyTextfield extends React.Component {
//     render () {
//         return <input type='text'/>;
//     }
// }

var MyButton = React.createClass({
    render: function() {
        return <button>{this.props.textlabel}</button>;
    }
});

var MyLabel = React.createClass({
    render: function() {
        return <div>{this.props.text}</div>;
    }
});

// FOr an example that has more features than this (e.g. event handling)
// http://jsfiddle.net/davidwaterston/7a3xxLtw/

var MyPulldown = React.createClass({
    _selectionChanged: function (e) {
        console.log("In selectionChanged");
        console.log(e);
        console.log(this);
        console.log(this.props.onChange);
        console.log("XXX");
        if (this.props.onChange) {
            this.props.onChange(e)
        }
    },
    _selectStyle: {width: 'auto'},
    render: function() {
        var opts =  [];
        var i = 1;
        for(var opt of this.props.options ) {
            var ovalu = opt.value;
            // compare the passed in selectedOption to the value of the option to see if there is a match
            if (this.props.selectedOption == ovalu )
                opts.push(<option key={i} value={opt.value}>{opt.label}</option>);
            else
                opts.push(<option key={i} value={opt.value}>{opt.label}</option>);
            i++;
        }

        return <div className="input-group">
                   <span className="input-group-addon">{this.props.label}</span>
                       <select id={this.props.myId} defaultValue={this.props.selectedOption} name={this.props.myName} onChange={this._selectionChanged} className="form-control" style={this._selectStyle}>{opts}</select>
        </div>;

    }
});





class Greeting extends React.Component {
    render() {
        return <h1>Hello there, {this.props.name}</h1>;
    }
}

function myFn (e) {

}

//  Mounting area

var TextLabel = 'Number of rows';

function getPulldownProps (eltId, options) {
    var obj = {id: eltId};
    obj.options = options;
    obj.label = document.getElementById(eltId).getAttribute("label");
    obj.myName = document.getElementById(eltId).getAttribute("myName");
    obj.selectedOption = document.getElementById(eltId).getAttribute("selectedOption");
    return obj;
}

function mountPulldownComponent (mountingEltId, options) {
    var elt = document.getElementById(mountingEltId);
    if (elt) {
        var myprops = getPulldownProps(mountingEltId, options);
        React.render(
            <div>

                <MyPulldown myName={myprops.myName} label={myprops.label} options={myprops.options}
                            selectedOption={myprops.selectedOption} onChange={(e) => myFn(e) }/>

            </div>,
            document.getElementById(mountingEltId)
        );
    }

}



mountPulldownComponent('my-pulldown1',[{label: 'Has Audio', value:'hasAudio'}, {label: 'No Audio', value: 'noAudio'}]);
mountPulldownComponent('my-pulldown2',[{value:'multichoice',label:'Multiple Choice'}, {value:'shortanswer',label:'Short Answer'}]);
mountPulldownComponent('my-pulldown3',[{value:'ready',label:'Ready'}, {value:'testable',label:'Testable'}, {value:'dead',label:'Dead'}]);

// MyPulldown.testMethod('hi there');
React.render(<div><Greeting text="hi"/></div>, document.getElementById("greet"));
