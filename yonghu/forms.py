# -*- coding: utf-8 -*-
from django import forms
from yonghu.models import User


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'password', 'icon', 'age', 'sex']

    password2 = forms.CharField(max_length=128)
    #用于验证两次密码是否一致。
    def clean_password2(self):
        #super有个clean方法。就是处理后的数据。将数据转换成python的格式。
        cleaned_data = super(RegisterForm,self).clean()
        #cleaned是一个字典，直接取出来即可。
        if cleaned_data['password'] != cleaned_data['password2']:
            raise forms.ValidationError('两次输入的密码不一致')
