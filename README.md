🎵 SoundForest – Sistema de Recomendação de Músicas
📌 Objetivo do Sistema

O objetivo do SoundForest é recomendar músicas personalizadas para o usuário com base nos gêneros musicais que ele informa inicialmente e no feedback dado (avaliações de 1 a 5 estrelas).
O sistema aprende progressivamente: quanto mais o usuário avalia músicas, mais precisas (e diversas) se tornam as recomendações.


⚙️ Como Executar
🔹 Backend (FastAPI)

Entre na pasta backend

Instale as dependências:

pip install -r requirements.txt


Execute o servidor:

uvicorn main:app --reload --port 8000


O backend ficará disponível em http://127.0.0.1:8000

🔹 Frontend (Streamlit)

Entre na pasta frontend

Ative o ambiente virtual (se configurado)

Execute o app:

streamlit run app.py


Acesse a interface no navegador em http://localhost:8501

🧠 Lógica de Recomendação

O usuário seleciona gêneros iniciais → o sistema gera músicas relacionadas e pelo menos uma surpresa (de outro gênero).

O usuário avalia músicas de 1⭐ a 5⭐ → os pesos dos gêneros são ajustados:

4 ou 5 estrelas aumentam a chance de recomendar mais músicas desse gênero.

As recomendações combinam:

Filtragem colaborativa baseada em usuários (usando correlação de Pearson para medir similaridade).

Ajuste por pesos de gênero (boost controlado para evitar dominância de um único estilo).

📐 Justificativa da Métrica de Similaridade

A métrica escolhida foi a correlação de Pearson, porque:

Mede a relação linear entre as avaliações de dois usuários.

Considera não só os valores absolutos das notas, mas também suas variações em relação à média de cada usuário.

É adequada em cenários onde diferentes usuários têm escalas de avaliação distintas (uns dão notas mais altas, outros mais baixas).

📊 Cálculo e Análise da Acurácia

A acurácia é medida conforme a orientação do guia:

Divide-se as avaliações de cada usuário em treino (70%) e teste (30%).

As recomendações são geradas com base no treino.

Verifica-se quantas músicas do conjunto de teste aparecem nas recomendações.

📌 Exemplo (hipotético):

Usuário avaliou 20 músicas, sendo 6 no conjunto de teste.

Sistema recomendou 10 músicas.

Dessas, 3 estavam no conjunto de teste.

➡️ Acurácia = 3 / 10 = 0,3 (30%)


Renato Barbosa 
Pedro Yutaro
Ryan Marinho