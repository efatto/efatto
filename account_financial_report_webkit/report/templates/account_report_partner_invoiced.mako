<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            ${css}

            .list_table .act_as_row {
                margin-top: 10px;
                margin-bottom: 10px;
                font-size:10px;
            }

            .account_line {
                font-weight: bold;
                font-size: 15px;
                background-color:#F0F0F0;
            }

            .account_line .act_as_cell {
                height: 30px;
                vertical-align: bottom;
            }

        </style>
    </head>
    <body>
        <%!
        def amount(text):
            return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
        %>

        <%setLang(user.lang)%>

        <div class="act_as_table data_table">
            <div class="act_as_row labels">
                <div class="act_as_cell">${_('Chart of Account')}</div>
                <div class="act_as_cell">${_('Fiscal Year')}</div>
                <div class="act_as_cell">
                    %if filter_form(data) == 'filter_date':
                        ${_('Dates Filter')}
                    %else:
                        ${_('Periods Filter')}
                    %endif
                </div>
                <!--div class="act_as_cell">${_('Accounts Filter')}</div-->
                <div class="act_as_cell">${_('Target Moves')}</div>
            </div>
            <div class="act_as_row">
                <div class="act_as_cell">${ chart_account.name }</div>
                <div class="act_as_cell">${ fiscalyear.name if fiscalyear else '-' }</div>
                <div class="act_as_cell">
                    ${_('From:')}
                    %if filter_form(data) == 'filter_date':
                        ${formatLang(start_date, date=True) if start_date else u'' }
                    %else:
                        ${start_period.name if start_period else u''}
                    %endif
                    ${_('To:')}
                    %if filter_form(data) == 'filter_date':
                        ${ formatLang(stop_date, date=True) if stop_date else u'' }
                    %else:
                        ${stop_period.name if stop_period else u'' }
                    %endif
                </div>
                <!--div class="act_as_cell">
                    %if accounts(data):
                        ${', '.join([account.code for account in accounts(data)])}
                    %else:
                        ${_('All')}
                    %endif
                </div-->
                <div class="act_as_cell">${ display_target_move(data) }</div>
            </div>
        </div>

        %if not display_only_total(data):
        %for current_account in objects:
        %if len(ledger_lines[current_account.id].get(current_account.id, [])) > 0:
            <%
            total_invoiced = 0.0
            %>

            <div class="account_title bg" style="margin-top: 20px; font-size: 12px; width: 690px;">${current_account.code} - ${current_account.name}</div>

            <div class="act_as_table list_table">

                <div class="act_as_thead">
                    <div class="act_as_row labels">
                        ## account name
                        ##<div class="act_as_cell" style="width: 80px;">${_('Account / Partner Name')}</div>
                        ## code
                        ##<div class="act_as_cell first_column" style="width: 20px;">${_('Code / Ref')}</div>
                        ## invoice date
                        <div class="act_as_cell" style="width: 80px;">${_('Invoice date')}</div>
                        ## invoice number
                        <div class="act_as_cell" style="width: 80px;">${_('Invoice n.')}</div>
                        ## invoiced
                        <div class="act_as_cell amount" style="width: 30px;">${_('Invoiced')}</div>
                    </div>
                </div>

                <div class="act_as_tbody">

                    %for line in ledger_lines[current_account.id].get(current_account.id, []):
                        <%
                        total_invoiced += line.get('amount_untaxed_signed')
                        %>
                        <div class="act_as_row lines">
                            <div class="act_as_cell first_column">${formatLang(line.get('date_invoice'), date=True) or u'' }</div>
                            <div class="act_as_cell first_column">${line.get('internal_number') }</div>
                            <div class="act_as_cell amount">${formatLang(line.get('amount_untaxed_signed')) | amount}</div>
                        </div>
                    %endfor

                </div>
                <div class="act_as_tfoot" style="margin-top:5px;">
                    <div class="act_as_row labels" style="font-weight: bold; font-size: 11x;">
                        ## account name
                        <div class="act_as_cell">${current_account.name}</div>
                        ## code
                        <div class="act_as_cell first_column">${current_account.code}</div>
                        ## debit
                        <div class="act_as_cell amount">${formatLang(total_invoiced) | amount}</div>
                    </div>
                </div>
            </div>
        %endif
        %endfor
        %endif

        %if display_only_total(data):
        <%
        general_total_invoiced = 0.0
        %>
            <div class="act_as_table list_table">

                <div class="act_as_thead">
                    <div class="act_as_row labels">
                        ## account name
                        <div class="act_as_cell" style="width: 80px;">${_('Account / Partner Name')}</div>
                        ## account vat
                        <div class="act_as_cell first_column" style="width: 20px;">${_('Code / Ref')}</div>
                        ## invoice date
                        <div class="act_as_cell" style="width: 80px;">${_('VAT')}</div>
                        ## invoice number
                        <div class="act_as_cell" style="width: 80px;">${_('C.F.')}</div>
                        ## invoiced
                        <div class="act_as_cell amount" style="width: 30px;">${_('Invoiced')}</div>
                    </div>
                </div>
                <div class="act_as_tbody">
        %for current_account in objects:
        %if len(ledger_lines[current_account.id].get(current_account.id, [])) > 0:
            <%
            total_invoiced = 0.0
            %>
                %for line in ledger_lines[current_account.id].get(current_account.id, []):
                    <%
                    total_invoiced += line.get('amount_untaxed_signed')
                    general_total_invoiced += line.get('amount_untaxed_signed')
                    %>
                %endfor
                    <div class="act_as_row lines">
                        <div class="act_as_cell first_column">${current_account.name}</div>
                        <div class="act_as_cell first_column">${current_account.code}</div>
                        <div class="act_as_cell first_column">${ledger_lines[current_account.id].get('vat', '')}</div>
                        <div class="act_as_cell first_column">${ledger_lines[current_account.id].get('fiscalcode', '')}</div>
                        <div class="act_as_cell amount">${formatLang(total_invoiced) | amount}</div>
                    </div>

        %endif
        %endfor
                </div>
                <div class="act_as_tfoot" style="margin-top:5px;">
                    <div class="act_as_row labels" style="font-weight: bold; font-size: 11x;">
                        ## account name
                        <div class="act_as_cell">Totals</div>
                        <div class="act_as_cell first_column"></div>
                        <div class="act_as_cell first_column"></div>
                        <div class="act_as_cell first_column"></div>
                        ## debit
                        <div class="act_as_cell amount">${formatLang(general_total_invoiced) | amount}</div>
                    </div>
                </div>
            </div>
        %endif

    </body>
</html>
