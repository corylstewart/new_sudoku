class FixFormat:
    def fix_greeks_format(self, greeks):
        #format the different values for a clean view on the webapp
        new_greeks = {}
        for option in greeks:
            new_greeks[option] = {}
            new_greeks[option]['call'] = {}
            new_greeks[option]['put'] = {}
            new_greeks[option]['call']['value'] = format(greeks[option]['call']['value'], '.2f')
            new_greeks[option]['call']['delta'] = format(greeks[option]['call']['delta'], '.2f')
            new_greeks[option]['call']['theta'] = format(greeks[option]['call']['theta'], '.3f')
            new_greeks[option]['call']['gamma'] = format(greeks[option]['call']['gamma'], '.3f')
            new_greeks[option]['call']['vega'] = format(greeks[option]['call']['vega'], '.3f')
            new_greeks[option]['put']['value'] = format(greeks[option]['put']['value'], '.2f')
            new_greeks[option]['put']['delta'] = format(greeks[option]['put']['delta'], '.2f')
            new_greeks[option]['put']['theta'] = format(greeks[option]['put']['theta'], '.3f')
            new_greeks[option]['put']['gamma'] = format(greeks[option]['put']['gamma'], '.3f')
            new_greeks[option]['put']['vega'] = format(greeks[option]['put']['vega'], '.3f')
        return new_greeks

    def fix_expiration_totals_format(self, expiration_totals):
        formatted_expiration_totals = {}
        for exp in expiration_totals:
            formatted_expiration_totals[exp] = {}
            formatted_expiration_totals[exp]['vega'] = format(expiration_totals[exp]['vega'], '.0f')
            formatted_expiration_totals[exp]['delta'] = format(expiration_totals[exp]['delta'], '.0f')
            formatted_expiration_totals[exp]['gamma'] = format(expiration_totals[exp]['gamma'], '.0f')
            formatted_expiration_totals[exp]['theta'] = format(expiration_totals[exp]['theta'], '.0f')
        return formatted_expiration_totals

    def fix_postition_totals_format(self, position_totals):
        formatted_position_totals = {}
        formatted_position_totals['vega'] = format(position_totals['vega'], '.0f')
        formatted_position_totals['delta'] = format(position_totals['delta'], '.0f')
        formatted_position_totals['gamma'] = format(position_totals['gamma'], '.0f')
        formatted_position_totals['theta'] = format(position_totals['theta'], '.0f')
        return formatted_position_totals