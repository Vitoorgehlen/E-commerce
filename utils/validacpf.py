def validacpf(cpf):
    cpf = str(cpf)

    if len(cpf) != 11:
        print("Não possui 11 caracteres")
        return False
 
    if cpf == cpf[0] * 11:
        print("CPF inválido")
        return False

    nove_digitos_cpf = cpf[:9]
    contador_regressivo = 10
    resultado_digito_1 = 0

    for digito in nove_digitos_cpf:
        resultado_digito_1 += int(digito) * contador_regressivo
        contador_regressivo-=1

    resultado_digito_1 = (resultado_digito_1 * 10) % 11

    if resultado_digito_1 > 9:
        digito_1 = 0
    else:
        digito_1 = resultado_digito_1

    dez_digitos_cpf = nove_digitos_cpf + str(digito_1)
    contador_regressivo_2 = 11
    resultado_digito_2 = 0

    for digito in dez_digitos_cpf:
        resultado_digito_2 += int(digito) * contador_regressivo_2
        contador_regressivo_2 -= 1

    resultado_digito_2 = (resultado_digito_2 * 10) % 11

    if resultado_digito_2 > 9:
        digito_2 = 0
    else:
        digito_2 = resultado_digito_2
    
    cpf_gerado_pelo_calculo = f"{nove_digitos_cpf}{digito_1}{digito_2}"

    if cpf == cpf_gerado_pelo_calculo:
        print("O CPF é válido")
        return True
    else: 
        print("O CPF inválido")
        return False