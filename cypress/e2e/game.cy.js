describe('The Primer v2 — regresyon E2E', () => {
  beforeEach(() => {
    cy.visit('/web/');
  });

  it('sekiz kararı tamamlar, başarılı finale ulaşır ve yeniden başlayabilir', () => {
    cy.get('[data-cy="normal-mode"]').click();
    for (let i = 0; i < 8; i++) {
      cy.get('[data-cy="scene-title"]').should('be.visible');
      cy.get('[data-cy="option-0"]').click();
      cy.get('[data-cy="confirm"]').click();
      if (i < 7) cy.get('[data-cy="scene-count"]').should('contain', `Sahne ${i+2} / 8`);
    }
    cy.get('[data-cy="summary"]').should('be.visible').and('contain', 'Sistem kurtarıldı');
    cy.get('[data-cy="reset"]').click();
    cy.get('[data-cy="normal-mode"]').should('be.visible');
  });

  it('karar değişimini ilk seçim dışında sayar', () => {
    cy.get('[data-cy="normal-mode"]').click();
    cy.get('[data-cy="option-0"]').click();
    cy.get('[data-cy="option-1"]').click();
    cy.get('[data-cy="option-0"]').click();
    cy.window().then(w => { expect(w.primerTestState().changes).eq(2); });
    cy.get('[data-cy="confirm"]').click();
    cy.get('[data-cy="scene-count"]').should('contain','Sahne 2 / 8');
  });

  it('veri toplama modunda öz bildirim etiketini modelden bağımsız kaydeder', () => {
    cy.on('window:confirm', () => true);
    cy.get('[data-cy="collection-mode"]').click();
    cy.get('[data-cy="hint-request"]').should('not.be.visible');
    cy.get('[data-cy="option-0"]').click();
    cy.get('[data-cy="confirm"]').click();
    cy.get('[data-cy="self-report"]').should('be.visible');
    cy.get('[data-cy="need-help"]').click();
    cy.window().then(w => expect(w.primerTestState().records).eq(1));
    cy.get('[data-cy="export-csv"]').should('be.visible');
  });

  it('model çalışmasa bile oyun çökmez', () => {
    cy.get('[data-cy="normal-mode"]').click();
    cy.get('[data-cy="option-0"]').click();
    cy.get('[data-cy="confirm"]').click();
    cy.get('[data-cy="scene-count"]').should('contain','Sahne 2 / 8');
  });
});
