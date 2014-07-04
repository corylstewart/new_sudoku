
function getIRate() {
    var p = document.params;
    var ir = document.irate;
    ir.daysexp.value = p.daysexp.value;
    ir.strike.value = p.strike.value;
    ir.submit();
}

function selectDaysToExp() {
    var d = document.params;
    for (i = 0; i < d.expdate.options.length; i++)
        if (d.expdate.options[i].value == d.daysexp.value) {
            d.expdate.options[i].selected = true;
            return;
        }
    d.expdate.options[d.expdate.options.length - 1].selected = true;
}


function calcGrek(o, a) {
    var s = document.sender;
    var p = document.params;
    s.days.value = document.grek.days.value;
    s.price.value = p.price.value;
    s.strike.value = p.strike.value;
    s.A.value = a;
    s.country.value = p.country.value;
    s.divyield.value = p.divyield.value
    s.daysexp.value = p.daysexp.value
    s.vola.value = p.vola.value
    s.intrate.value = p.intrate.value;
    if (p.freq) {
        s.freq.value = p.freq.value;
        s.divlastdate.value = p.divlastdate.value;
    }

    document.sender.submit();
}

function calcIV(o) {
    var s = document.sender;
    var i = document.ivola;
    s.opt_price.value = i.opt_price.value;
    s.tp.value = i.tp.options[i.tp.selectedIndex].value;
    calcGrek(document.params, 1);
}

function daystoexp() {
    var d = document.params;
    if (d.expdate != null && d.expdate.options[d.expdate.selectedIndex].value != -1)
        d.daysexp.value = d.expdate.options[d.expdate.selectedIndex].value;
}

function inc(obj, value, d) {
    if (obj.value != "") {
        obj.value = Math.round((parseFloat(obj.value) + value * d) * 10000) / 10000;
        clrR();
    }
}
function strikev(obj) {
    v = parseFloat(obj.value);
    if (v < 50) return 2.5;
    if (v <= 200) return 5;
    return 10;
}
function clrR() {
    var o = document.grek;
    o.oprice_c.value = '0.0000';
    o.delta_c.value = '0.0000';
    o.gamma_c.value = '0.0000';
    o.theta_c.value = '0.0000';
    o.vega_c.value = '0.0000';
    o.rho_c.value = '0.0000';
    o.oprice_p.value = '0.0000';
    o.delta_p.value = '0.0000';
    o.gamma_p.value = '0.0000';
    o.theta_p.value = '0.0000';
    o.vega_p.value = '0.0000';
    o.rho_p.value = '0.0000';
    o.symbol_c.value = 'N/A';
    o.symbol_p.value = 'N/A';
}
