interface AIThoughtStep {
  text: string;
  emoji: string;
  type: 'analyzing' | 'considering' | 'connecting' | 'concluding';
}

interface AIThoughtPattern {
  steps: AIThoughtStep[];
  finalResponse: {
    text: string;
    emoji: string;
  };
}

interface SelectionContext {
  currentSelection: string;
  previousSelections: string[];
  roundNumber: number;
  playerName: string;
  isSkipped?: boolean;
}

export class AIConversationGenerator {
  private skipThoughts = {
    analyzing: [
      "Wait... {PLAYER} just skipped this round? 🤨",
      "Hold up, {PLAYER} is avoiding making a choice...",
      "Interesting... {PLAYER} decided to skip... 🙈",
      "Oh no! {PLAYER} is running away from decisions!",
      "Skipping detected! What is {PLAYER} hiding? 👀",
      "Avoidance mode activated by {PLAYER}...",
      "Skip button pressed! Emergency analysis needed! 🚨",
    ],
    considering: [
      "This skipping pattern is telling me something...",
      "Maybe {PLAYER} is overwhelmed by choices? 🤯",
      "Could this be decision paralysis or pure chaos? 🎪",
      "The skip strategy... bold or just lazy? 🤔",
      "Is {PLAYER} testing my patience? Because it's working! 😅",
      "Skip after skip... I'm starting to see a pattern here...",
      "This avoidance behavior is fascinating! 🧐",
    ],
    connecting: [
      "Actually... maybe {PLAYER} is just mysterious! 🕵️‍♂️",
      "Wait, what if this is strategic skipping? 🧠",
      "Or perhaps {PLAYER} is saving energy for something big? ⚡",
      "Could this be the skip-master technique? 🥷",
      "Actually, maybe {PLAYER} just likes chaos! 🌪️",
      "Hold on... is {PLAYER} trying to break my AI brain? 🤖💥",
      "Plot twist: The skips ARE the personality! 🎭",
    ],
    concluding: [
      "Yep, {PLAYER} is definitely the skipping type! 🦘",
      "Confirmed: {PLAYER} lives life on skip mode! ⏭️",
      "The skips have spoken! {PLAYER} is pure chaos! 🌀",
      "Analysis complete: {PLAYER} is a beautiful mystery! 💫",
      "Final verdict: {PLAYER} is the skip champion! 🏆",
      "It's official - {PLAYER} has mastered the art of avoidance! 🎯",
      "Case closed: {PLAYER} is wonderfully unpredictable! 🎲",
    ]
  };

  private thinkingSteps = {
    analyzing: [
      "Interesting... {PLAYER} chose {SELECTION}...",
      "Let me analyze this choice of {SELECTION}...",
      "Hmm, {SELECTION}... what does this tell me?",
      "Processing {SELECTION} selection from {PLAYER}...",
      "Diving deep into the {SELECTION} choice...",
      "This {SELECTION} pick is revealing...",
      "Examining the {SELECTION} preference...",
    ],
    
    considering: [
      "Given their history of {HISTORY}, this makes sense...",
      "Connecting {SELECTION} with their previous {LAST_CHOICE}...",
      "This builds on their {LAST_CHOICE} from before...",
      "I'm seeing a pattern with {HISTORY} and now {SELECTION}...",
      "The {SELECTION} choice after {LAST_CHOICE} is telling...",
      "Considering how {SELECTION} fits with {HISTORY}...",
      "This {SELECTION} adds to their {LAST_CHOICE} personality...",
    ],

    connecting: [
      "Actually, let me reconsider this...",
      "Wait, there's more to this...",
      "But hold on, what if...",
      "Something else comes to mind...",
      "Actually, I'm getting a different vibe...",
      "Let me think about this differently...",
      "There's another angle here...",
      "Hold that thought... I'm sensing...",
    ],

    concluding: [
      "Yes! The {SELECTION} choice confirms it...",
      "Perfect! {SELECTION} is exactly right for {PLAYER}...",
      "This {SELECTION} selection seals the deal...",
      "Absolutely! {SELECTION} completes the picture...",
      "I've got it! {SELECTION} is the key...",
      "Crystal clear now - {SELECTION} tells the story...",
      "Everything clicks with this {SELECTION} choice...",
    ]
  };

  private finalResponses = {
    Adventure: {
      positive: [
        "You're definitely an adventure seeker! Bold and fearless! 🚀",
        "I see a thrill-seeker who embraces the unknown! 💥",
        "Adventure flows through your veins! You're unstoppable! ⚡",
        "Your adventurous spirit shines bright! Ready for anything! 🌟",
        "Bold choice! You're someone who makes things happen! 🎯",
      ],
      thoughtful: [
        "Adventure speaks to your brave heart... 🦸‍♂️",
        "The adventurer in you is calling the shots! 🗻",
        "I sense someone who writes their own story... 📖",
        "Your inner explorer is guiding these choices! 🧭",
      ]
    },
    
    Classic: {
      positive: [
        "Timeless elegance! You have impeccable taste! ✨",
        "Classic choice - you appreciate the finer things! 👑",
        "Sophisticated and refined! Pure class! 🎭",
        "You know quality when you see it! Elegant soul! 💎",
        "Timeless beauty - you're drawn to what endures! 🏛️",
      ],
      thoughtful: [
        "Classic resonates with your refined nature... 🎼",
        "There's wisdom in choosing the timeless path... 📚",
        "Your appreciation for classics shows depth... 🍷",
        "Traditional values guide your heart... 💫",
      ]
    },

    Light: {
      positive: [
        "Fresh and balanced! You bring harmony everywhere! 🌿",
        "Light and bright - you're pure sunshine! ☀️",
        "Balance is your superpower! Perfectly calibrated! ⚖️",
        "You have that fresh perspective we all need! 🍃",
        "Light choice shows your optimistic spirit! 🌈",
      ],
      thoughtful: [
        "Light speaks to your gentle nature... 🕊️",
        "You seek balance in all things... 🧘‍♀️",
        "There's wisdom in choosing lightness... 🦋",
        "Your fresh outlook is refreshing... 🌅",
      ]
    },

    Rich: {
      positive: [
        "You embrace life's rich experiences! Depth seeker! 🍫",
        "Rich choice - you don't settle for shallow! 💎",
        "Intensity is your middle name! Deep and meaningful! 🌊",
        "You live life in full color! Rich and vibrant! 🎨",
        "Complex flavors for a complex soul! Beautiful! 🍷",
      ],
      thoughtful: [
        "Rich resonates with your depth... 🌌",
        "You appreciate life's deeper meanings... 📜",
        "Complexity calls to your sophisticated side... 🎭",
        "Your taste for richness shows character... 💫",
      ]
    },

    Smooth: {
      positive: [
        "Smooth operator! You appreciate finesse! 🎯",
        "Elegance in motion! You flow like silk! 💫",
        "Refined taste! You're all about that smooth life! ✨",
        "Grace and poise - that's your signature! 🩰",
        "Smooth choice shows your sophisticated side! 🥂",
      ],
      thoughtful: [
        "Smooth speaks to your refined soul... 🌙",
        "You value elegance over chaos... 🦢",
        "There's poetry in your smooth preference... 📝",
        "Your appreciation for finesse is admirable... 🎼",
      ]
    },

    Crunchy: {
      positive: [
        "Texture lover! You embrace life's surprises! 🎉",
        "Crunchy choice - you're full of delightful surprises! 🥜",
        "You love variety and excitement! Never boring! 🎪",
        "Complex and interesting - just like your personality! 🌟",
        "Texture adds spice to life! You get it! 🎊",
      ],
      thoughtful: [
        "Crunchy reflects your multifaceted nature... 🔮",
        "You appreciate life's varied textures... 🍂",
        "Complexity is your comfort zone... 🧩",
        "Your love for variety shows creativity... 🎨",
      ]
    },

    Sprinkles: {
      positive: [
        "Playful spirit detected! Life's a celebration! 🎊",
        "Sprinkles everywhere! You bring joy to everything! 🌈",
        "Pure fun energy! You light up every room! ✨",
        "Colorful soul! You make life more vibrant! 🎨",
        "Party time! You're the fun everyone needs! 🎉",
      ],
      thoughtful: [
        "Sprinkles show your playful heart... 🦄",
        "You believe life should be celebrated... 🎭",
        "Your joyful spirit is infectious... 🌟",
        "Color and fun guide your choices... 🎪",
      ]
    },

    Caramel: {
      positive: [
        "Sweet sophistication! You know true quality! 🍯",
        "Caramel wisdom - you appreciate the golden moments! ✨",
        "Smooth and sweet! Perfect combination! 👌",
        "Golden choice! You have exquisite taste! 🏆",
        "Caramel soul - warm, sweet, and sophisticated! 💛",
      ],
      thoughtful: [
        "Caramel speaks to your warm nature... 🌅",
        "You find sweetness in sophistication... 🍷",
        "Golden moments are your specialty... ⭐",
        "Your refined sweetness is rare... 🌙",
      ]
    }
  };

  generateConversation(context: SelectionContext): AIThoughtPattern {
    const { currentSelection, previousSelections, roundNumber, playerName, isSkipped } = context;
    
    // If skipped, use skip thoughts
    if (isSkipped) {
      return this.generateSkipConversation(context);
    }
    
    // Determine number of steps (2-4 steps)
    const stepCount = 2 + Math.floor(Math.random() * 3);
    const steps: AIThoughtStep[] = [];
    
    // Always start with analyzing
    steps.push({
      text: this.getRandomTemplate('analyzing', context),
      emoji: this.getAnalyzingEmoji(),
      type: 'analyzing'
    });

    // Add considering step if we have history
    if (previousSelections.length > 0 && stepCount > 2) {
      steps.push({
        text: this.getRandomTemplate('considering', context),
        emoji: this.getConsideringEmoji(),
        type: 'considering'
      });
    }

    // Maybe add a connecting/rethinking step
    if (stepCount > 3 && Math.random() > 0.4) {
      steps.push({
        text: this.getRandomTemplate('connecting', context),
        emoji: this.getConnectingEmoji(),
        type: 'connecting'
      });
    }

    // Always end with concluding
    steps.push({
      text: this.getRandomTemplate('concluding', context),
      emoji: this.getConcludingEmoji(),
      type: 'concluding'
    });

    // Generate final response
    const responseType = Math.random() > 0.3 ? 'positive' : 'thoughtful';
    const finalResponse = {
      text: this.getFinalResponse(currentSelection, responseType),
      emoji: this.getSelectionEmoji(currentSelection)
    };

    return { steps, finalResponse };
  }

  private generateSkipConversation(context: SelectionContext): AIThoughtPattern {
    const stepCount = 2 + Math.floor(Math.random() * 3);
    const steps: AIThoughtStep[] = [];
    
    // Start with skip analyzing
    steps.push({
      text: this.getRandomSkipTemplate('analyzing', context),
      emoji: '🤨',
      type: 'analyzing'
    });

    // Add skip considering
    if (stepCount > 2) {
      steps.push({
        text: this.getRandomSkipTemplate('considering', context),
        emoji: '🙃',
        type: 'considering'
      });
    }

    // Maybe add skip connecting
    if (stepCount > 3) {
      steps.push({
        text: this.getRandomSkipTemplate('connecting', context),
        emoji: '🤷‍♂️',
        type: 'connecting'
      });
    }

    // End with skip concluding
    steps.push({
      text: this.getRandomSkipTemplate('concluding', context),
      emoji: '🦘',
      type: 'concluding'
    });

    const finalResponse = {
      text: "Skip detected! You're beautifully unpredictable! 🎪",
      emoji: '🙈'
    };

    return { steps, finalResponse };
  }

  private getRandomSkipTemplate(type: keyof typeof this.skipThoughts, context: SelectionContext): string {
    const templates = this.skipThoughts[type];
    const template = templates[Math.floor(Math.random() * templates.length)];
    return this.replacePlaceholders(template, context);
  }

  private getRandomTemplate(type: keyof typeof this.thinkingSteps, context: SelectionContext): string {
    const templates = this.thinkingSteps[type];
    const template = templates[Math.floor(Math.random() * templates.length)];
    
    return this.replacePlaceholders(template, context);
  }

  private replacePlaceholders(template: string, context: SelectionContext): string {
    const { currentSelection, previousSelections, playerName } = context;
    
    let result = template
      .replace(/{SELECTION}/g, currentSelection)
      .replace(/{PLAYER}/g, playerName);

    if (previousSelections.length > 0) {
      const lastChoice = previousSelections[previousSelections.length - 1];
      const history = previousSelections.length > 1 
        ? `${previousSelections.slice(0, -1).join(' and ')} and ${lastChoice}`
        : lastChoice;
      
      result = result
        .replace(/{LAST_CHOICE}/g, lastChoice)
        .replace(/{HISTORY}/g, history);
    }

    return result;
  }

  private getFinalResponse(selection: string, type: 'positive' | 'thoughtful'): string {
    const responses = this.finalResponses[selection as keyof typeof this.finalResponses] || this.finalResponses.Classic;
    const responseArray = responses[type];
    return responseArray[Math.floor(Math.random() * responseArray.length)];
  }

  private getAnalyzingEmoji(): string {
    const emojis = ['🤔', '🧐', '👀', '💭', '🔍', '🎯'];
    return emojis[Math.floor(Math.random() * emojis.length)];
  }

  private getConsideringEmoji(): string {
    const emojis = ['🤨', '💡', '🧠', '⚡', '🔗', '🎪'];
    return emojis[Math.floor(Math.random() * emojis.length)];
  }

  private getConnectingEmoji(): string {
    const emojis = ['💫', '🌟', '✨', '🎭', '🔮', '🌈'];
    return emojis[Math.floor(Math.random() * emojis.length)];
  }

  private getConcludingEmoji(): string {
    const emojis = ['💥', '🎊', '✅', '🎯', '👏', '🏆'];
    return emojis[Math.floor(Math.random() * emojis.length)];
  }

  private getSelectionEmoji(selection: string): string {
    const emojiMap: { [key: string]: string } = {
      Adventure: '🚀',
      Classic: '👑',
      Light: '🌿',
      Rich: '🍫',
      Smooth: '✨',
      Crunchy: '🥜',
      Sprinkles: '🌈',
      Caramel: '🍯'
    };
    return emojiMap[selection] || '🎯';
  }
}

export const aiConversationGenerator = new AIConversationGenerator();