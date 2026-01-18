# 📋 Frontend - Décisions Clés

> Journal des choix architecturaux et techniques pour le frontend Smart Meeting Scribe.
> Format inspiré des ADR (Architecture Decision Records).

---

## Index des décisions

| ID | Titre | Date | Statut |
|----|-------|------|--------|
| [D001](#d001-fetch-natif-au-lieu-daxios) | Fetch natif au lieu d'Axios | 17 Jan 2026 | ✅ Adopté |
| [D002](#d002-html5-natif-pour-audiovideo-mvp) | HTML5 natif pour Audio/Video | 17 Jan 2026 | ✅ Adopté |
| [D003](#d003-pattern-hybride-pour-les-composants) | Pattern hybride composants | 17 Jan 2026 | ✅ Adopté |
| [D004](#d004-pas-de-confirmation-email-mvp) | Pas de confirmation email | 17 Jan 2026 | ✅ Adopté |
| [D005](#d005-mobile-reporté-à-phase-4) | Mobile reporté à Phase 4+ | 17 Jan 2026 | ✅ Adopté |
| [D006](#d006-groupes-gérés-par-admin-phase-2) | Groupes gérés par Admin | 17 Jan 2026 | ⏳ Reporté |
| [D007](#d007-shadcnui-comme-librairie-de-composants) | shadcn/ui comme lib composants | 17 Jan 2026 | ✅ Adopté |

---

## [D001] Fetch natif au lieu d'Axios

**Date** : 17 Jan 2026  
**Statut** : ✅ Adopté

**Contexte** :  
Next.js 16 recommande `fetch` natif pour bénéficier du caching automatique et de la compatibilité Server Components. Axios est vu comme "l'ancienne façon de faire".

**Décision** :  
Utiliser `fetch` avec un wrapper custom (`lib/api.ts`) + `XMLHttpRequest` uniquement pour l'upload (progress bar).

**Conséquences** :  
- ✅ Moins de dépendances (-15kb bundle)
- ✅ Plus aligné avec les patterns Next.js modernes
- ⚠️ Upload progress nécessite du code XMLHttpRequest dédié

---

## [D002] HTML5 natif pour Audio/Video (MVP)

**Date** : 17 Jan 2026  
**Statut** : ✅ Adopté

**Contexte** :  
Howler.js (~15kb) et Video.js (~100kb) sont des librairies lourdes pour des features avancées (waveform, HLS, etc.) dont le MVP n'a pas besoin.

**Décision** :  
MVP utilise `<audio controls>` et `<video controls>` HTML5 natif via un composant `MediaPlayer.tsx` simple.

**Conséquences** :  
- ✅ 0kb ajouté au bundle
- ✅ Fonctionnalités de base (play, pause, seek) suffisantes
- ⚠️ Features avancées (playback speed, waveform) reportées à Phase 2+ si nécessaire

---

## [D003] Pattern hybride pour les composants

**Date** : 17 Jan 2026  
**Statut** : ✅ Adopté

**Contexte** :  
Besoin d'une organisation scalable sans sur-ingénierie pour un projet de taille moyenne.

**Décision** :  
```
components/
├── ui/          # shadcn (ne pas modifier)
├── common/      # réutilisables sur 2+ pages
├── layout/      # structure app (Sidebar, Header)
└── features/    # par domaine métier (meetings, upload, chat)
```

**Règle simple** : Si un composant est utilisé sur 2+ pages → `common/`. Sinon → `features/{domain}/`.

**Conséquences** :  
- ✅ Organisation claire et prévisible
- ✅ Facile pour un nouveau développeur ou une IA de s'y retrouver
- ✅ Scalable pour les phases futures

---

## [D004] Pas de confirmation email (MVP)

**Date** : 17 Jan 2026  
**Statut** : ✅ Adopté

**Contexte** :  
L'application est destinée à un usage interne/entreprise, pas au grand public.

**Décision** :  
Register simple : email + password + confirm password. Redirect vers `/login` après inscription. Pas de mail de confirmation.

**Conséquences** :  
- ✅ Implémentation plus rapide
- ✅ Pas besoin d'infrastructure email pour le MVP
- ⚠️ À réévaluer si l'application devient publique ou SaaS

---

## [D005] Mobile reporté à Phase 4+

**Date** : 17 Jan 2026  
**Statut** : ✅ Adopté

**Contexte** :  
Les utilisateurs cibles sont principalement sur desktop (poste de travail bureau).

**Décision** :  
Focus desktop-first. Pas de responsive design pour le MVP. Mobile prévu en Phase 4 ou ultérieur ("v1000").

**Conséquences** :  
- ✅ Développement plus rapide
- ✅ Moins de tests cross-device
- ⚠️ L'app ne sera pas utilisable confortablement sur mobile

---

## [D006] Groupes gérés par Admin (Phase 2)

**Date** : 17 Jan 2026  
**Statut** : ⏳ Reporté

**Contexte** :  
Le CRUD des groupes (création, modification, suppression) nécessite une réflexion sur les rôles/permissions utilisateurs.

**Décision** :  
Reporter la gestion des groupes à une section Admin en Phase 2+. Pour le MVP, le groupe "Tous" existe par défaut (seed data) et les autres groupes peuvent être créés via API.

**Conséquences** :  
- ✅ MVP plus simple et focalisé
- ⚠️ Utilisateurs ne peuvent pas créer de groupes via l'UI en Phase 1

---

## [D007] shadcn/ui comme librairie de composants

**Date** : 17 Jan 2026  
**Statut** : ✅ Adopté

**Contexte** :  
Besoin de composants UI accessibles, customizables, et bien intégrés avec Tailwind.

**Décision** :  
Utiliser shadcn/ui. Les composants sont copiés dans `components/ui/` et peuvent être customisés. Lucide Icons inclus.

**Conséquences** :  
- ✅ Composants accessibles (WCAG)
- ✅ Thème dark-first facile à implémenter
- ✅ Pas de dépendance runtime (code copié, pas importé)

---

## Template pour nouvelles décisions

```markdown
## [D0XX] Titre de la décision

**Date** : JJ MMM AAAA  
**Statut** : ✅ Adopté | ⏳ Reporté | ❌ Rejeté | 🔄 Remplacé par Dxxx

**Contexte** :  
Pourquoi cette décision a dû être prise ? Quel problème résout-elle ?

**Décision** :  
Qu'avons-nous décidé de faire ?

**Conséquences** :  
- ✅ Avantages
- ⚠️ Points d'attention / Trade-offs
- ❌ Ce qu'on perd
```

---

*Dernière mise à jour : 17 Janvier 2026*
