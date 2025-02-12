import click


class FadnOptionRequiredIf(click.Option):
    """
    Custom class that inherits from click.Option in order to extend its functionality.
    """
    def full_process_value(self, ctx, value):
        """
        Function that applies Required If logic to the certain Click Option.
        :param ctx: native Click's class object Context.
        :param value: value of the Click's Option that was marked by this function.
        :return: value itself when none of the conditions raised an error.
        """
        value = super(FadnOptionRequiredIf, self).full_process_value(ctx, value)

        if value is None and ctx.params['stage'] == 'all':
            msg = 'Required if --stage=all'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        return value


class GenericGraphUriOptionRequiredIf(click.Option):
    """
    Custom class that inherits from click.Option in order to extend its functionality.
    """
    def full_process_value(self, ctx, value):
        """
        Function that applies Required If logic to the certain Click Option.
        :param ctx: native Click's class object Context.
        :param value: value of the Click's Option that was marked by this function.
        :return: value itself when none of the conditions raised an error.
        """
        value = super(GenericGraphUriOptionRequiredIf, self).full_process_value(ctx, value)

        if value is None and 'load' in ctx.params['process']:
            msg = 'Required if --process=load'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        return value


class GenericInputTypeOptionRequiredIf(click.Option):
    """
    Custom class that inherits from click.Option in order to extend its functionality.
    """
    def full_process_value(self, ctx, value):
        """
        Function that applies Required If logic to the certain Click Option.
        :param ctx: native Click's class object Context.
        :param value: value of the Click's Option that was marked by this function.
        :return: value itself when none of the conditions raised an error.
        """
        value = super(GenericInputTypeOptionRequiredIf, self).full_process_value(ctx, value)

        if value is None and 'transform' in ctx.params['process']:
            msg = 'Required if --process=transform'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        elif value is None and 'preprocess' in ctx.params['process']:
            msg = 'Required if --process=preprocess'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        elif value is None and 'mapping' in ctx.params['process']:
            msg = 'Required if --process=mapping'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        return value


class GenericMappingInputDirOptionRequiredIf(click.Option):
    """
    Custom class that inherits from click.Option in order to extend its functionality.
    """
    def full_process_value(self, ctx, value):
        """
        Function that applies Required If logic to the certain Click Option.
        :param ctx: native Click's class object Context.
        :param value: value of the Click's Option that was marked by this function.
        :return: value itself when none of the conditions raised an error.
        """
        value = super(GenericMappingInputDirOptionRequiredIf, self).full_process_value(ctx, value)

        if value is None and 'transform' in ctx.params['process'] and 'mapping' not in ctx.params['process']\
                and ctx.params['dir_input']:
            msg = 'Required if --process=transform'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        return value


class GenericMappingInputUrlOptionRequiredIf(click.Option):
    """
    Custom class that inherits from click.Option in order to extend its functionality.
    """
    def full_process_value(self, ctx, value):
        """
        Function that applies Required If logic to the certain Click Option.
        :param ctx: native Click's class object Context.
        :param value: value of the Click's Option that was marked by this function.
        :return: value itself when none of the conditions raised an error.
        """
        value = super(GenericMappingInputUrlOptionRequiredIf, self).full_process_value(ctx, value)

        if value is None and 'transform' in ctx.params['process'] and 'mapping' not in ctx.params['process']\
                and ctx.params['url_input']:
            msg = 'Required if --process=transform'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        return value


class GenericBaseUriOptionRequiredIf(click.Option):
    """
    Custom class that inherits from click.Option in order to extend its functionality.
    """
    def full_process_value(self, ctx, value):
        """
        Function that applies Required If logic to the certain Click Option.
        :param ctx: native Click's class object Context.
        :param value: value of the Click's Option that was marked by this function.
        :return: value itself when none of the conditions raised an error.
        """
        value = super(GenericBaseUriOptionRequiredIf, self).full_process_value(ctx, value)
        if value is None and 'mapping' in ctx.params['process'] and not (ctx.params.get('yarrrml_rules_value') or
                                                                         ctx.params.get('yarrrml_rules_url')):
            msg = 'Required if --process=mapping'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        elif value is None and 'transform' in ctx.params['process'] and 'mapping' not in ctx.params['process']:
            if ctx.params['input_type'] in ('Shapefile', 'GML', 'KML', 'GeoJson'):
                msg = f"Required with {ctx.params['input_type']} type of a file!"
                raise click.MissingParameter(ctx=ctx, param=self, message=msg)
            return value
        return value


class LpisOptionRequiredIf(click.Option):
    """
    Custom class that inherits from click.Option in order to extend its functionality.
    """
    def full_process_value(self, ctx, value):
        """
        Function that applies Required If logic to the certain Click Option.
        :param ctx: native Click's class object Context.
        :param value: value of the Click's Option that was marked by this function.
        :return: value itself when none of the conditions raised an error.
        """
        value = super(LpisOptionRequiredIf, self).full_process_value(ctx, value)

        if value is None and ctx.params['stage'] == 'all':
            msg = 'Required if --stage=all'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        return value


class LpisCountryOptionRequiredIf(click.Option):
    """
    Custom class that inherits from click.Option in order to extend its functionality.
    """
    def full_process_value(self, ctx, value):
        """
        Function that applies Required If logic to the certain Click Option.
        :param ctx: native Click's class object Context.
        :param value: value of the Click's Option that was marked by this function.
        :return: value itself when none of the conditions raised an error.
        """
        value = super(LpisCountryOptionRequiredIf, self).full_process_value(ctx, value)

        if value is None and ctx.params['stage'] == 'all':
            msg = 'Required if --stage=all'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        elif value is None and ctx.params['stage'] == 'mapping':
            msg = 'Required if --stage=mapping'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        elif value is None and ctx.params['stage'] == 'transform':
            msg = 'Required if --stage=transform'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        elif value is None and ctx.params['stage'] == 'postprocess':
            msg = 'Required if --stage=postprocess'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        return value
