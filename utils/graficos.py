def configurar_eixo_x(fig, periodo):

    if periodo in ['15 dias', '1 mês']:
        fig.update_xaxes(tickformat="%d/%m", dtick="D2")

    elif periodo == '4 meses':
        fig.update_xaxes(tickformat="%b/%Y", dtick="M1")

    elif periodo == '12 meses':
        fig.update_xaxes(tickformat="%b/%Y", dtick="M2")

    elif periodo == 'Série completa':
        fig.update_xaxes(tickformat="%Y", dtick="M12")
        
def hover(nome):
    return f'{nome}: %{{y:.2f}} m<extra></extra>'
