/* The Black and Scholes (1973) Stock option formula */

function BlackScholes(PutCallFlag, S, X, T, r, v) {

    var d1, d2;
    d1 = (Math.log(S / X) + (r + v * v / 2.0) * T) / (v * Math.sqrt(T));
    d2 = d1 - v * Math.sqrt(T);


    if (PutCallFlag == "C")
        return S * CND(d1) - X * Math.exp(-r * T) * CND(d2);
    else
        return X * Math.exp(-r * T) * CND(-d2) - S * CND(-d1);

}

/* The cummulative Normal distribution function: */

function CND(x) {

    var a1, a2, a3, a4, a5, k;

    a1 = 0.31938153, a2 = -0.356563782, a3 = 1.781477937, a4 = -1.821255978, a5 = 1.330274429;

    if (x < 0.0)
        return 1 - CND(-x);
    else
        k = 1.0 / (1.0 + 0.2316419 * x);
    return 1.0 - Math.exp(-x * x / 2.0) / Math.sqrt(2 * Math.PI) * k
    * (a1 + k * (-0.356563782 + k * (1.781477937 + k * (-1.821255978 + k * 1.330274429))));

}

function calc_greeks(CP, spot, strike, vol, t, r) {
    var o = {
        value: 0,
        spot_1: spot + .01,
        spot_2: spot + .02,
        value_spot_1: 0,
        value_spot_2: 0,
        delta: 0,
        delta_1: 0,
        gamma: 0,
        value_vega: 0,
        vol_1: vol*1.01,
        vega: 0,
        value_theta: 0,
        t_1: t - (1/(364*2)),
        theta: 0,
    }
    o.value = BlackScholes(CP, spot, strike, t, r, vol);
    o.value_spot_1 = BlackScholes(CP, o.spot_1, strike, t, r, vol);
    o.delta = interpolate(spot, o.spot_1, o.value, o.value_spot_1)
    o.value_spot_2 = BlackScholes(CP, o.spot_2, strike, t, r, vol);
    o.delta_1 = interpolate(o.spot_1, o.spot_2, o.value_spot_1, o.value_spot_2);
    o.gamma = interpolate(spot, o.spot_1, o.delta, o.delta_1);
    o.value_vega = BlackScholes(CP, spot, strike, t, r, o.vol_1);
    o.vega = interpolate(vol, o.vol_1, o.value, o.value_vega) / 100;
    o.value_theta = BlackScholes(CP, spot, strike, o.t_1, r, vol);
    o.theta = -1*interpolate(t, o.t_1,o.value, o.value_theta)/364;

    return o
}

function interpolate(spot1, spot2, val1, val2) {
    return (val2 - val1) / (spot2 - spot1)
}


function make_vol_skew() {
    var spot = parseFloat(document.getElementById('stock_price_id').value);
    for (option in option_chain) {
        if (option_chain[option]['CP'] == 'C') {
            var strike = parseFloat(option_chain[option]['strike_price']);
            var spot_vol = parseFloat(document.getElementById('spot_vol_'.concat(option_chain[option]['exp_date_str'])).value);
            var slope = parseFloat(document.getElementById('slope_'.concat(option_chain[option]['exp_date_str'])).value);
            var smile = parseFloat(document.getElementById('smile_'.concat(option_chain[option]['exp_date_str'])).value);
            var vol = spot_vol + (spot - strike) * slope + Math.abs(spot - strike) * smile
            var vol = spot_vol + (spot - strike) * slope + Math.abs(spot - strike) * smile
            elem = document.getElementById(option.concat('_vol'))
            if (elem) {
                elem.value = vol
            }
        }
    }
    place_greeks();
}

function calc_greeks2(option, CP, spot, strike, vol, t, r) {
    var o = {};
    o.price = spot;
    o.delta = strike;
    o.gamma = vol,
    o.theta = t;
    o.vega = r;

    return o;
}

function place_greeks() {
    var rate = document.getElementById('interest_rate_id').value;
    var price = document.getElementById('stock_price_id').value;
    var now = new Date();
    var today = new Date(now.toDateString());
    for (option in option_chain) {
        if (option_chain[option]['CP'] == 'C') {
            var f_option = option;
            var o_type = '_call';
        }
        else {
            var st = option.slice(0, -9);
            var end = option.slice(-8);
            var f_option = st.concat('C', end);
            var o_type = '_put';
        }
        if (!(price in greek_dictionary[option])) {
            greek_dictionary[option][price] = {};
        }
        if (!(rate in greek_dictionary[option][price])) {
            greek_dictionary[option][price][rate] = {};
        }
        var vol_elem = document.getElementById(f_option.concat('_vol'));
        if (vol_elem) {
            var vol = vol_elem.value;
            if (!(vol in greek_dictionary[option][price][rate])) {
                greek_dictionary[option][price][rate][vol] = {};
            }
            var exp_year = parseInt(option_chain[option]['exp_year']);
            var exp_month = parseInt(option_chain[option]['exp_month']);
            var exp_day = parseInt(option_chain[option]['exp_day']);
            var exp_date = new Date(option_chain[option]['js_date_str']);
            var t = (exp_date - today) / (1000 * 60 * 60 * 24 * 364);
            var t_str = toString(t);
            if (t_str in greek_dictionary[option][price][rate][vol]) {
                var this_option = greek_dictionary[option][price][rate][vol][time];
            }
            else {
                var strike = option_chain[option]['strike_price'];
                var this_option = calc_greeks(option_chain[option]['CP'], parseFloat(price), parseFloat(strike), parseFloat(vol), parseFloat(t), parseFloat(rate));
            }
            var elem_price = document.getElementById(option.concat(o_type, '_value'));
            if (elem_price) {
                elem_price.value = this_option.value.toFixed(3);
            }
            var elem_delta = document.getElementById(option.concat(o_type, '_delta'));
            if (elem_delta) {
                elem_delta.value = this_option.delta.toFixed(3);
            }
            var elem_vega = document.getElementById(option.concat(o_type, '_vega'));
            if (elem_vega) {
                elem_vega.value = this_option.vega.toFixed(4);
            }
            var elem_gamma = document.getElementById(option.concat(o_type, '_gamma'));
            if (elem_gamma) {
                elem_gamma.value = this_option.gamma.toFixed(4);
            }
            var elem_theta = document.getElementById(option.concat(o_type, '_theta'));
            if (elem_theta) {
                elem_theta.value = this_option.theta.toFixed(4);
            }
        }
    }
}

function get_price_from_bar_chart() {
    var elem = document.getElementsByClassName('headerPrice');
    if (elem) {
        var price_text = elem[0].firstChild.textContent.replace('$', '').replace(/\t/g, '');
        var stock_price_elem = document.getElementById('stock_price_id')
        if (stock_price_elem) {
            stock_price_elem.value = price_text;
        }
    }
}

function check_show_dividends() {
    var elem = document.getElementById('show_dividends');
    if (elem) {
        if (elem.checked) {
            var TF = 'none';
        }
        else {
            var TF = '';
        }
        for (var i = 0; i < projected_dividends.length; i++) {
            var row_elem = document.getElementById('dividend_row_'.concat(projected_dividends[i][0]));
            if (row_elem) {
                row_elem.style.display = TF;
            }
        }
    }
}

function check_use_random_ticks() {
    var elem = document.getElementById('use_random_ticks')
    setInterval(make_stock_tick, 1000);

    function make_stock_tick() {
        if (elem) {
            if (elem.checked) {
                var tick_range = 5;
                var price_elem = document.getElementById('stock_price_id');
                var tick = (Math.floor((Math.random() * (tick_range + 1) * 2) - tick_range)) / 100;
                spot = parseFloat(price_elem.value) + tick;
                if (spot <= 0) {
                    spot = .01
                }
                price_elem.value = spot.toFixed(2);
                do_stock_tick();
            }
            else {
                clearInterval()
            }
        }
    }
}

function check_show_strike() {
    for (var i = 0; i < ordered_option_symbol_list.length; i++) {
        var option = ordered_option_symbol_list[i];
        var limit_strikes_check = document.getElementById('show_limited_strikes')
        var this_exp = option_chain[option]["exp_date_str"];
        var exp_elem = document.getElementById(this_exp.concat('_checkbox'));
        var this_row = document.getElementById(option.concat('_row'));
        var this_strike = document.getElementById(option.concat('_call_delta'));
        if (exp_elem && this_row && this_strike && limit_strikes_check) {
            var delta = this_strike.value;
            var disp = 'none'
            if (((delta < .75 && delta > .25) || !limit_strikes_check.checked) && exp_elem.checked) {
                disp = ''
            }
            this_row.style.display = disp;
        }
    }
}

function calc_position_greeks() {
    var position_dictionary = { 'totals': { 'vega': 0, 'delta': 0, 'gamma': 0, 'theta': 0 } };
    for (exp in vols_by_month) {
        position_dictionary[exp] = { 'vega': 0, 'delta': 0, 'gamma': 0, 'theta': 0 };
    }
    for (option in option_chain) {
        if (option.slice(-9, -8) == 'C') {
            var CP = '_call';
        }
        else {
            var CP = '_put';
        }
        var this_pos = document.getElementById(option.concat(CP, '_position'));
        if (this_pos) {
            var option_pos = parseInt(this_pos.value)
            if (option_pos != 0) {
                var exp = option_chain[option]['exp_date_str']
                position_dictionary[exp]['vega'] += option_pos * parseFloat(document.getElementById(option.concat(CP, '_vega')).value)*100;
                position_dictionary[exp]['delta'] += (option_pos * parseFloat(document.getElementById(option.concat(CP, '_delta')).value))*100;
                position_dictionary[exp]['gamma'] += option_pos * parseFloat(document.getElementById(option.concat(CP, '_gamma')).value)*100;
                position_dictionary[exp]['theta'] += option_pos * parseFloat(document.getElementById(option.concat(CP, '_theta')).value)*100;
            }
        }
    }
    for (exp in vols_by_month) {
        for (greek in position_dictionary[exp]) {
            position_dictionary['totals'][greek] += position_dictionary[exp][greek];
        }
    }
    var stock_pos = document.getElementById('stock_position');
    if (stock_pos) {
        position_dictionary['totals']['delta'] += parseFloat(stock_pos.value);
    }
    for (exp in vols_by_month) {
        document.getElementById('vega_'.concat(exp)).value = position_dictionary[exp]['vega'].toFixed(3)
        document.getElementById('delta_'.concat(exp)).value = position_dictionary[exp]['delta'].toFixed(0)
        document.getElementById('gamma_'.concat(exp)).value = position_dictionary[exp]['gamma'].toFixed(3)
        document.getElementById('theta_'.concat(exp)).value = position_dictionary[exp]['theta'].toFixed(3)
    }
    document.getElementById('vega_total').value = position_dictionary['totals']['vega'].toFixed(3)
    document.getElementById('delta_total').value = position_dictionary['totals']['delta'].toFixed(0)
    document.getElementById('gamma_total').value = position_dictionary['totals']['gamma'].toFixed(3)
    document.getElementById('theta_total').value = position_dictionary['totals']['theta'].toFixed(3)

}

function do_everything() {
    make_vol_skew();
    place_greeks();
    check_show_dividends();
    check_show_strike();
    check_use_random_ticks();
    calc_position_greeks();
}

function do_stock_tick() {
    place_greeks();
    calc_position_greeks();
}