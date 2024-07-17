from core.views import BaseFormView
from django.urls import reverse
from report_a_suspected_breach import forms

#     Conditionals supplied_to and made_available


class WhereWereTheGoodsSuppliedFromView(BaseFormView):
    form_class = forms.WhereWereTheGoodsSuppliedFromForm

    def get_success_url(self) -> str:
        success_paths = {
            "about_the_supplier": ["different_uk_address", "outside_the_uk"],
            "where_were_the_goods_supplied_to": ["same_address", "do_not_know"],
            "where_were_the_goods_made_available_from": ["they_have_not_been_supplied"],
        }
        form_data = self.form.cleaned_data.get("where_were_the_goods_supplied_from")
        for path, choices in success_paths.items():
            if form_data in choices:
                return reverse(f"report_a_suspected_breach:{path}")


# option 1
#  if other
# about the supplier
# if same or i dont know
# where were the goods supplied to
# about the end user
# you've added end user
# were there any other addresses?
# end

# option 2 - not supplied yet
# made available from
# same address
#  made available to
# end user if not i dont know
# were there any other addresses?
# end


# option 3

# class AboutTheSupplierView(BaseFormView):
#     form_class = forms.AboutTheSupplierForm
#
#     def get_success_url(self):
#
#         pass
#
# class WhereWereTheGoodsMadeAvailableView(BaseFormView):
#     form_class = forms.WhereWereTheGoodsSuppliedFromForm
#     success_url = reverse_lazy("report_a_suspected_breach:about_the_supplier")
