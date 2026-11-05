describe('ONNX Runtime Web ↔ Python Oracle — diferansiyel test', () => {
  it('aynı 5 referans girdisi için fark < 1e-4', () => {
    cy.readFile('tests/parite.json').then(refs => {
      expect(refs.length).to.be.at.least(5);
      cy.visit('/web/');
      cy.get('#model-status', { timeout: 15000 }).should($el => {
        const text = $el.text();
        expect(text, 'Model status text: ' + text).to.contain('Model yüklendi');
      });
      cy.window().should(w => {
        expect(w.primerModelLoaded(), 'ONNX Runtime web gerçekte yüklenmeli').to.eq(true);
      }).then(async w => {
        // Her tahmin doğrudan gerçek web ONNX inference fonksiyonuna gider.
        for (const [index, ref] of refs.entries()) {
          const result = await w.primerRunInference(ref.input);
          expect(result, 'gerçek ONNX sonucu ' + (index+1)).to.be.a('number');
          const difference = Math.abs(result - ref.expected_proba);
          expect(difference, `referans ${index+1}; fark=${difference}`).to.be.lessThan(1e-4);
        }
      });
    });
  });
});
